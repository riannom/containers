#!/usr/bin/env python3
"""Offline Docker smoke test: Core REST, Electrs startup, and regtest indexing.

Run from the repository root with Python 3 and Docker Compose installed.
Uses disposable container filesystems, no host ports or app-data mounts.
"""
import json, os, subprocess, time, uuid

RUN_ID = uuid.uuid4().hex[:10]

def run(*args, check=True, **kw):
 r = subprocess.run(args, text=True, capture_output=True, **kw)
 if check and r.returncode: raise RuntimeError(r.stderr + r.stdout)
 return r
def config(kind, network):
 env=dict(os.environ, APP_DATA_DIR='/unused-smoke-data', NETWORK_IP='10.21.0.0', DEVICE_DOMAIN_NAME='localhost')
 cmd=f'source containers-bitcoin-{network}/exports.sh; source containers-electrs-{network}/exports.sh; docker compose -f containers-{kind}-{network}/docker-compose.yml config --no-consistency --format json'
 return json.loads(run('bash','-c',cmd,env=env).stdout)['services']
def rpc(core, e, chain, *args, check=True):
 return run('docker','exec',core,'bitcoin-cli',f'-chain={chain}',f'-rpcport={e["RPC_PORT"]}',f'-rpcuser={e["RPC_USER"]}',f'-rpcpassword={e["RPC_PASS"]}',*args,check=check)
def start(name, image, env, command, network='none'):
 args=['docker','run','-d','--name',name,'--network',network]
 for k,v in env.items(): args+=['-e',f'{k}={v}']
 args+=['--entrypoint','sh',image,'-c',command]
 run(*args)
def node(core, code):
 return run('docker','exec',core,'node','-e',code).stdout
for network,chain in [('signet','signet'),('testnet3','test'),('testnet4','testnet4'),('signet','regtest')]:
 core=f'electrs-test-{RUN_ID}-core-{chain}'; electrs=f'electrs-test-{RUN_ID}-index-{chain}'
 cs=config('bitcoin',network)[network+'_server']; es=config('electrs',network)['electrs_'+network]
 ce=cs['environment']; ce['BITCOIND_IP']='127.0.0.1';ce['DEFAULT_CHAIN']=chain
 ee=es['environment'];ee['ELECTRS_DAEMON_RPC_ADDR']='127.0.0.1:'+ce['RPC_PORT']
 ee['ELECTRS_NETWORK']='regtest' if chain=='regtest' else ee['ELECTRS_NETWORK']
 try:
  start(core,cs['image'],ce,'mkdir -p /data/bitcoin; exec node dist/server.js')
  for _ in range(40):
   info=rpc(core,ce,chain,'getblockchaininfo',check=False)
   if info.returncode==0:break
   time.sleep(1)
  assert info.returncode==0,info.stderr
  rest=node(core,f"fetch('http://127.0.0.1:{ce['RPC_PORT']}/rest/chaininfo.json').then(async r=>{{if(!r.ok)throw Error(r.status);console.log(await r.text())}})")
  assert json.loads(rest)['chain']==chain
  if chain=='regtest':
   rpc(core,ce,chain,'createwallet','upgrade-test')
   address=rpc(core,ce,chain,'getnewaddress').stdout.strip()
   rpc(core,ce,chain,'generatetoaddress','101',address)
  # Seed an old index sentinel; verify the upgrade never writes into this directory.
  command='mkdir -p /data/db; echo keep-old-index > /data/db/rollback-sentinel; '+es['command'][0].replace('$$', '$')
  start(electrs,es['image'],ee,command,'container:'+core)
  port=ee['ELECTRS_MONITORING_ADDR'].split(':')[-1]
  for _ in range(40):
   state=run('docker','inspect','-f','{{.State.Running}}',electrs).stdout.strip()
   if state!='true':raise RuntimeError(run('docker','logs',electrs).stderr[-4000:])
   metrics=run('docker','exec',core,'node','-e',f"fetch('http://127.0.0.1:{port}/').then(async r=>{{if(!r.ok)throw Error(r.status); console.log(await r.text())}})",check=False)
   if metrics.returncode==0:break
   time.sleep(1)
  assert metrics.returncode==0,metrics.stderr
  time.sleep(2)
  logs=run('docker','logs',electrs).stderr
  assert 'Starting electrs 0.12.0' in logs,logs
  assert run('docker','inspect','-f','{{.State.Running}}',electrs).stdout.strip()=='true',logs
  if chain=='regtest':
   wallet_port=ee['ELECTRS_ELECTRUM_RPC_ADDR'].split(':')[-1]
   code="""const net=require('net');const s=net.connect(PORT,'127.0.0.1',()=>s.write(JSON.stringify({id:1,method:'blockchain.headers.subscribe',params:[]})+'\\n'));let b='';s.setTimeout(5000,()=>{s.destroy();process.exit(1)});s.on('error',()=>process.exit(1));s.on('data',d=>{b+=d;if(b.includes('\\n')){console.log(b.split('\\n')[0]);s.end();}});""".replace('PORT',wallet_port)
   for _ in range(40):
    reply=run('docker','exec',core,'node','-e',code,check=False)
    if reply.returncode==0 and reply.stdout:break
    time.sleep(1)
   assert json.loads(reply.stdout)['result']['height']==101,reply.stdout
  assert run('docker','exec',electrs,'cat','/data/db/rollback-sentinel').stdout.strip()=='keep-old-index'
  assert run('docker','exec',electrs,'test','-d','/data/db-v0.12').returncode==0
  print(f'{chain}: Core REST, Electrs 0.12 startup/metrics, separate index passed'+('; Electrum protocol indexed height 101' if chain=='regtest' else ''),flush=True)
 finally:
  for name in [electrs,core]:
   run('docker','stop','-t','15',name,check=False);run('docker','rm','-v',name,check=False)
