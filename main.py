import asyncio
import aiohttp
import json
import os
import sys
import time
import traceback
import random
import base64
import uuid
import requests
import threading
import websocket
import websockets
import websockets.exceptions as ws_exc
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from colorama import init, Fore
from tls_client import Session

init(autoreset=True)

# ═══════════════════════════════════════════════════════
# RAILWAY ENV VARS
# ═══════════════════════════════════════════════════════
INVITE_CODE     = os.environ.get("INVITE_CODE", "")
GUILD_ID        = os.environ.get("GUILD_ID", "")
VC_CHANNEL_ID   = os.environ.get("VC_CHANNEL_ID", "")
TEXT_CHANNEL_ID = os.environ.get("TEXT_CHANNEL_ID", "")
MUTE_COUNT      = int(os.environ.get("MUTE_COUNT", "0"))
VIDEO_COUNT     = int(os.environ.get("VIDEO_COUNT", "0"))
STREAM_COUNT    = int(os.environ.get("STREAM_COUNT", "0"))
CHAT_DELAY      = int(os.environ.get("CHAT_DELAY", "5"))
SMART_CHAT      = os.environ.get("SMART_CHAT", "true").lower() != "false"
ENABLE_VC       = os.environ.get("ENABLE_VC", "false").lower() == "true"
ENABLE_CHAT     = os.environ.get("ENABLE_CHAT", "false").lower() == "true"
ENABLE_QUESTS   = os.environ.get("ENABLE_QUESTS", "true").lower() != "false"

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE, "config.json")
TOKENS_FILE = os.path.join(BASE, "tokens.txt")
_hdr_cache = None
_hdr_time = 0

# ═══════════════════════════════════════════════════════
# LOGGER
# ═══════════════════════════════════════════════════════
_print_lock = threading.Lock()
bGRN="\x1b[92m";bRED="\x1b[91m";bYEL="\x1b[93m";bCYN="\x1b[96m";bWHT="\x1b[97m"
ORG="\x1b[38;5;208m";GRN="\x1b[32m";RED="\x1b[31m"
R="\x1b[0m";B="\x1b[1m";D="\x1b[2m"

def _ts(): return f"{D}[{bWHT}{datetime.now().strftime('%H:%M:%S')}{D}]{R}"
def _log(pc,p, mc,m, dt=None):
    with _print_lock:
        print(f"{_ts()}  {pc}{B}{p}{R}  {mc}{m}{R}{f'  {D}{dt}{R}' if dt else ''}")
def L_success(t,m,d=None): _log(bGRN,"(+)",bWHT,m,d)
def L_error(t,m,d=None): _log(bRED,"(-)",bWHT,m,d)
def L_warning(t,m,d=None): _log(ORG,"(*)",bWHT,m,d)
def L_info(t,m,d=None): _log(bCYN,"(i)",bWHT,m,d)

# ═══════════════════════════════════════════════════════
# ANSI HELPERS (for main.py display)
# ═══════════════════════════════════════════════════════
def c(r,g,b): return f"\033[38;2;{r};{g};{b}m"
EMBER=[(255,60,0),(255,100,10),(255,140,30),(255,180,60),(255,210,90)]
LAVA=[(140,0,0),(200,10,0),(255,30,0),(255,70,20),(255,110,40)]
MINT=[(0,200,120),(30,230,140),(80,255,170),(140,255,200),(200,255,230)]
GOLD=[(180,120,0),(210,150,10),(240,180,20),(255,210,40),(255,230,80)]
PURPLE=[(80,0,120),(110,20,160),(140,40,200),(170,80,230),(200,120,255)]

def gradient(text,pal):
    out=[]
    for li,l in enumerate(text.split("\n")):
        if not l: out.append(""); continue
        n=len(l); mid=len(pal)
        col=""
        for i,ch in enumerate(l):
            idx=min(int(i/max(n,1)*mid),mid-1)
            r,g,b=pal[idx]
            col+=f"\033[38;2;{r};{g};{b}m{ch}"
        out.append(col+R)
    return "\n".join(out)

def box(title,pal):
    w=50; pad=(w-len(title)-2)//2
    print(f"\n  {D}{'═'*w}{R}")
    print(f"  {D}║{' '*pad}{B}{gradient(title,pal)}{R}{' '*(w-pad-len(title)-2)}{D}║{R}")
    print(f"  {D}{'═'*w}{R}\n")

def divider(): print(f"  {D}{'·'*48}{R}")
def log_info(m): print(f"  {c(100,200,255)}(i){R}  {m}")
def log_ok(m): print(f"  {c(0,255,120)}(+){R}  {m}")
def log_warn(m): print(f"  {c(255,200,50)}(*){R}  {m}")
def log_fail(m): print(f"  {c(255,50,50)}(-){R}  {m}")
def spin_result(m,pal): print(f"\n  {B}{gradient('>> '+m,pal)}{R}\n")

# ═══════════════════════════════════════════════════════
# CLIENT — DiscordREST & GatewayClient
# ═══════════════════════════════════════════════════════
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9215 Chrome/138.0.7204.251 Electron/37.6.0 Safari/537.36"
API_BASE = "https://discord.com/api/v10"
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
XSUP = base64.b64encode(json.dumps({
    "os":"Windows","browser":"Discord Client","release_channel":"stable",
    "client_version":"1.0.9215","os_version":"10.0.19045","os_arch":"x64",
    "app_arch":"x64","system_locale":"en-US","has_client_mods":False,
    "client_build_number":471091,"native_build_number":72186,
}, separators=(',',':')).encode()).decode()

class DiscordREST:
    def __init__(self,token):
        self.token=token
        self._session=Session(client_identifier="chrome_120",random_tls_extension_order=True)
    def _h(self,extra=None):
        h={"Authorization":self.token,"Content-Type":"application/json","User-Agent":USER_AGENT,"X-Super-Properties":XSUP,"Accept":"*/*","Accept-Language":"en-US","Origin":"https://discord.com","Referer":"https://discord.com/channels/@me","Sec-Fetch-Dest":"empty","Sec-Fetch-Mode":"cors","Sec-Fetch-Site":"same-origin","x-debug-options":"bugReporterEnabled","x-discord-locale":"en-US","x-super-properties":XSUP}
        if extra: h.update(extra)
        return h
    def _req(self,method,path,body=None,params=None,retries=3,delay=0.5):
        url=API_BASE+path
        for a in range(retries):
            try:
                if method=="GET": r=self._session.get(url,headers=self._h(),params=params)
                elif method=="POST": r=self._session.post(url,headers=self._h(),json=body)
                elif method=="PATCH": r=self._session.patch(url,headers=self._h(),json=body)
                else: raise ValueError(f"Unknown method: {method}")
                sc=r.status_code
                if sc==429:
                    try: ra=r.json().get("retry_after",2)
                    except: ra=2
                    time.sleep(float(ra)); continue
                if sc in(500,502,503,504):
                    time.sleep(delay*(a+1)); continue
                if sc==204: return {}
                if sc in(200,201):
                    try: return r.json()
                    except: return {}
                try: rj=r.json()
                except: rj={}
                err=Exception(rj.get("message",f"HTTP {sc}"))
                err.status=sc; err.body=rj; raise err
            except Exception as e:
                if hasattr(e,'status'): raise
                if a<retries-1: time.sleep(delay); continue
                raise
        raise Exception("Max retries exceeded")
    def get(self,path,params=None): return self._req("GET",path,params=params)
    def post(self,path,body=None): return self._req("POST",path,body=body)
    def patch(self,path,body=None): return self._req("PATCH",path,body=body)

class GatewayClient:
    def __init__(self,token):
        self.token=token; self.ws=None; self._seq=None; self._hb_timer=None
        self._hb_interval=None; self._connected=threading.Event()
        self._ready_data=None; self._error=None; self._closed=False; self._thread=None
    def connect(self,timeout=30):
        self._thread=threading.Thread(target=self._run,daemon=True)
        self._thread.start()
        ok=self._connected.wait(timeout=timeout)
        if not ok: self.destroy(); raise TimeoutError("Gateway connect timeout")
        if self._error: raise self._error
        return self._ready_data
    def destroy(self):
        self._closed=True
        if self._hb_timer: self._hb_timer.cancel(); self._hb_timer=None
        if self.ws:
            try: self.ws.close()
            except: pass
    def _run(self):
        try:
            hdrs={"User-Agent":USER_AGENT,"Accept-Language":"en-US","Cache-Control":"no-cache","Pragma":"no-cache"}
            self.ws=websocket.WebSocketApp(GATEWAY_URL,header=[f"{k}: {v}" for k,v in hdrs.items()],on_message=self._on_msg,on_error=self._on_err,on_close=self._on_cls)
            self.ws.run_forever(ping_interval=0,ping_timeout=None)
        except Exception as e:
            self._error=e; self._connected.set()
    def _on_msg(self,ws,raw):
        try: p=json.loads(raw)
        except: return
        op=p.get("op");d=p.get("d");s=p.get("s");t=p.get("t")
        if s is not None: self._seq=s
        if op==10:
            interval=d["heartbeat_interval"]/1000.0; self._hb_interval=interval
            jitter=random.random()*interval
            self._hb_timer=threading.Timer(jitter,self._hb_loop)
            self._hb_timer.daemon=True; self._hb_timer.start()
            self._send_id()
        elif op==11: pass
        elif op==0 and t=="READY":
            self._ready_data=d; self._connected.set()
        elif op==9:
            self._error=Exception("Invalid Session"); self._connected.set(); self.destroy()
    def _on_err(self,ws,error):
        self._error=Exception(str(error)); self._connected.set()
    def _on_cls(self,ws,code,msg):
        if not self._connected.is_set(): self._error=Exception(f"WS closed {code}"); self._connected.set()
    def _hb_loop(self):
        if self._closed: return
        self._send_hb()
        if self._hb_interval:
            self._hb_timer=threading.Timer(self._hb_interval,self._hb_loop)
            self._hb_timer.daemon=True; self._hb_timer.start()
    def _send_hb(self):
        try:
            if self.ws: self.ws.send(json.dumps({"op":1,"d":self._seq}))
        except: pass
    def _send_id(self):
        payload={"op":2,"d":{"token":self.token,"capabilities":30717,"properties":{"os":"Windows","browser":"Discord Client","release_channel":"stable","client_version":"1.0.9215","os_version":"10.0.19045","os_arch":"x64","app_arch":"x64","system_locale":"en-US","has_client_mods":False,"browser_user_agent":USER_AGENT,"browser_version":"37.6.0","client_build_number":471091,"native_build_number":72186},"presence":{"status":"online","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{}}}}
        try:
            if self.ws: self.ws.send(json.dumps(payload))
        except: pass

# ═══════════════════════════════════════════════════════
# QUEST MODULE — Quest, QuestManager, Enroll, Bot, Completer
# ═══════════════════════════════════════════════════════

def _sleep(s): time.sleep(s)
def _retry(fn,retries=3,delay=0.5):
    last=None
    for i in range(retries):
        try: return fn()
        except Exception as e:
            last=e; status=getattr(e,"status",0); body=getattr(e,"body",{}) or {}
            if status==429 or status>=500:
                ra=body.get("retry_after",delay*(i+1))
                _sleep(float(ra)); continue
            raise
    raise last

class Quest:
    def __init__(self,data): self._d=data
    @classmethod
    def create(cls,data): return cls(data)
    @property
    def id(self): return self._d["id"]
    @property
    def config(self): return self._d["config"]
    @property
    def user_status(self): return self._d.get("user_status") or {}
    def quest_name(self): return self.config.get("messages",{}).get("quest_name","?")
    def game_title(self): return self.config.get("messages",{}).get("game_title","")
    def app_name(self): return self.config.get("application",{}).get("name","")
    def app_id(self): return self.config.get("application",{}).get("id","")
    def is_expired(self):
        try:
            exp=self.config["expires_at"]
            dt=datetime.fromisoformat(exp.replace("Z","+00:00"))
            return datetime.now(timezone.utc)>dt
        except: return False
    def isCompleted(self): return bool(self.user_status.get("completed_at"))
    def isEnrolledQuest(self): return bool(self.user_status.get("enrolled_at"))
    def hasClaimedRewards(self): return bool(self.user_status.get("claimed_at"))
    def updateUserStatus(self,data):
        if data: self._d["user_status"]=data.get("user_status",data)
    def task_info(self):
        us=self.user_status; cfg_task=self.config.get("task_config",{}).get("tasks",{})
        if not us.get("task"):
            for k,v in cfg_task.items():
                return (k,v.get("target",0),us.get("progress",{}).get(k,{}).get("value",0))
        tid=us["task"]["type"]; need=us["task"].get("target",0)
        done=us.get("progress",{}).get(tid,{}).get("value",0)
        return (tid,need,done)

class QuestManager:
    def __init__(self,rest,quests): self._rest=rest; self._quests=quests
    @classmethod
    def fromResponse(cls,rest,resp):
        qs=[Quest.create(q) for q in resp.get("quests",[])]
        return cls(rest,qs)
    def list(self): return self._quests
    def filterQuestsValid(self,questIds):
        excludedNames=["SPOTIFY_NEW","NETFLIX"]
        result=[]
        for q in self._quests:
            if q.is_expired() or q.hasClaimedRewards(): continue
            if questIds and q.id not in questIds: continue
            gt=q.game_title().upper(); qn=q.quest_name().upper()
            if any(n in gt or n in qn for n in excludedNames): continue
            features=q.config.get("features",[])
            tasks=q.config.get("task_config",{}).get("tasks",{})
            VIDEO_TASKS={"WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE"}
            has_video=any(k in VIDEO_TASKS and tasks[k] is not None for k in tasks)
            if has_video or 15 in features: result.append(q)
        return result
    def acceptQuest(self,quest):
        def _do():
            r=self._rest.post(f"/quests/{quest.id}/enroll",body={"location":11,"is_targeted":False,"metadata_raw":None})
            quest.updateUserStatus(r); return r
        return _retry(_do)
    def doingQuest(self,quest,accountIdentifier):
        questName=quest.quest_name()
        if not quest.isEnrolledQuest():
            try: self.acceptQuest(quest); _sleep(1.0)
            except Exception as e: L_error("",f"Enroll failed | Quest: {questName} | Account: {accountIdentifier}"); return
        try:
            us=_retry(lambda: self._rest.get(f"/quests/{quest.id}/user-status"))
            if us: quest.updateUserStatus(us)
        except: pass
        task_name,secondsNeeded,secondsDone=quest.task_info()
        if not task_name:
            features=quest.config.get("features",[])
            if 15 in features:
                task_name="WATCH_VIDEO"; secondsDone=0; secondsNeeded=0
                for k,v in quest.user_status.get("progress",{}).items():
                    if isinstance(v,dict):
                        secondsNeeded=v.get("target",0); secondsDone=v.get("value",0)
                        task_name=k if k in("WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE") else "WATCH_VIDEO"; break
                if not secondsNeeded: secondsNeeded=900
            else:
                L_warning("",f"No task | Quest: {questName}"); return
        if task_name in("WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE"):
            STEP=2
            def _build_ts(start,end):
                ts_list,cursor=[],start
                while cursor<end:
                    cursor=min(cursor+STEP,end)
                    ts_list.append(round((cursor+random.random()*0.1)*10)/10)
                if ts_list and ts_list[-1]!=float(end): ts_list.append(float(end))
                return ts_list
            def _reconnect():
                try:
                    gw=GatewayClient(self._rest.token); gw.connect(timeout=20); gw.destroy()
                except: pass
                _sleep(1.5)
            try: _retry(lambda: self._rest.post(f"/quests/{quest.id}/video-progress",body={"timestamp":1.0}))
            except Exception as e:
                if getattr(e,"status",0)==404: raise
            completed=False; max_retries=60; last_good_ts=secondsDone
            for attempt in range(max_retries):
                if completed: break
                try:
                    fresh=_retry(lambda: self._rest.get(f"/quests/{quest.id}/user-status"))
                    if fresh:
                        quest.updateUserStatus(fresh)
                        if fresh.get("completed_at"): completed=True; break
                        sv=fresh.get("progress",{})
                        for k in("WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE"):
                            v=sv.get(k,{}).get("value",0)
                            if v: last_good_ts=max(last_good_ts,v)
                except: pass
                if completed: break
                ts_list=_build_ts(last_good_ts,secondsNeeded); got_400=False
                for ts in ts_list:
                    if completed: break
                    try:
                        res=_retry(lambda ts=ts: self._rest.post(f"/quests/{quest.id}/video-progress",body={"timestamp":ts}))
                        if res:
                            quest.updateUserStatus(res); last_good_ts=ts
                            if res.get("completed_at"): completed=True; break
                    except Exception as e:
                        status=getattr(e,"status",0)
                        if status==404: raise
                        elif status==400: got_400=True; break
                        elif status!=429 and status<500: L_warning("",f"ts {ts} rejected ({status}) | Quest: {questName}")
                    _sleep(0.15+random.uniform(0,0.1))
                if completed: break
                if got_400: _reconnect()
                else:
                    for _ in range(5):
                        _sleep(1)
                        try:
                            st=_retry(lambda: self._rest.get(f"/quests/{quest.id}/user-status"))
                            if st and st.get("completed_at"): quest.updateUserStatus(st); completed=True; break
                        except: pass
                    if not completed and attempt<max_retries-1: _reconnect()
            if completed or quest.isCompleted(): L_success("",f"Quest done | Quest: {questName} | Account: {accountIdentifier}")
            else: L_error("",f"Quest incomplete | Quest: {questName} | Account: {accountIdentifier}")
        elif task_name=="PLAY_ON_DESKTOP":
            app_id=quest.app_id()
            while not quest.isCompleted() and not quest.is_expired():
                _,_,done=quest.task_info()
                if done>=secondsNeeded: break
                try:
                    res=_retry(lambda: self._rest.post(f"/quests/{quest.id}/heartbeat",body={"application_id":app_id,"terminal":False}))
                    if res: quest.updateUserStatus(res)
                except: break
                _sleep(30.0)
            try:
                res=_retry(lambda: self._rest.post(f"/quests/{quest.id}/heartbeat",body={"application_id":app_id,"terminal":True}))
                if res: quest.updateUserStatus(res)
            except: pass
            if quest.isCompleted(): L_success("",f"Quest done | Quest: {questName} | Account: {accountIdentifier}")
            else: L_error("",f"Quest incomplete | Quest: {questName} | Account: {accountIdentifier}")
        else: L_warning("",f"Unsupported task: '{task_name}' | Quest: {questName}")

# ── Enroll ──
def _parse_token(line):
    line=line.strip()
    if not line or line.startswith("#"): return ""
    if line.count(":")>=2: return ":".join(line.split(":")[2:]).strip()
    return line
def _load_tokens_from_file():
    try:
        with open(TOKENS_FILE,encoding="utf-8") as f:
            return list(dict.fromkeys(t for t in [_parse_token(l) for l in f] if t and len(t)>50))
    except: return []

def _enroll_token(token,index,questIds):
    rest=DiscordREST(token); gw=GatewayClient(token)
    try: gw.connect(timeout=30)
    except: pass
    finally: gw.destroy()
    for qid in questIds:
        try:
            try:
                rest.get(f"/quests/{qid}")
            except Exception as e:
                if getattr(e,"status",0)==404: continue
            time.sleep(0.3)
            rest.post(f"/quests/{qid}/enroll",body={"location":11,"is_targeted":False,"metadata_raw":None})
        except Exception as e:
            msg=str(e)
            if "already" not in msg.lower() and getattr(e,"status",0)!=400:
                L_warning("",f"Enroll failed → {qid} (# {index+1}): {msg}")

def _discover_quest_ids(token):
    rest=DiscordREST(token)
    try: resp=rest.get("/quests/@me")
    except Exception as e: L_warning("",f"Auto-discover failed: {e}"); return []
    ids=[]
    for q in resp.get("quests",[]):
        cfg=q.get("config",{}); us=q.get("user_status") or {}
        features=cfg.get("features",[]); tasks=cfg.get("task_config",{}).get("tasks",{})
        try:
            exp=cfg.get("expires_at","")
            if exp:
                dt=datetime.fromisoformat(exp.replace("Z","+00:00"))
                if datetime.now(timezone.utc)>dt: continue
        except: pass
        if us.get("completed_at"): continue
        VIDEO_TASKS={"WATCH_VIDEO","WATCH_VIDEO_ON_MOBILE"}
        has_video=any(k in VIDEO_TASKS and tasks.get(k) is not None for k in tasks)
        if has_video or 15 in features: ids.append(q["id"])
    return ids

def run_enroll(questIds,max_threads=5):
    if questIds is None: questIds=[]
    tokens=_load_tokens_from_file()
    if not tokens: return []
    if not questIds:
        L_info("","No quest_ids - auto-discovering...")
        questIds=_discover_quest_ids(tokens[0])
        if not questIds: L_warning("","No active video quests found"); return []
    L_info("",f"Enrolling {len(tokens)} tokens")
    with ThreadPoolExecutor(max_workers=max(1,max_threads)) as ex:
        futs=[ex.submit(_enroll_token,t,i,questIds) for i,t in enumerate(tokens)]
        for f in as_completed(futs):
            try: f.result()
            except: pass
    L_success("","Enroll done")
    return questIds

# ── Bot (quest runner) ──
SUCCESS_FILE=os.path.join(BASE,"success.txt")
_file_lock=threading.Lock()
_counter_lock=threading.Lock()

def _save_success(token):
    with _file_lock:
        try:
            with open(SUCCESS_FILE,"a",encoding="utf-8") as f: f.write(token+"\n")
        except: pass

def _login_account(token,index):
    short=token[:20]+"..."
    rest=DiscordREST(token); gw=GatewayClient(token)
    try:
        data=gw.connect(timeout=30)
        username=data.get("user",{}).get("username","?")
        L_success("",f"Login OK -> {short}")
        return {"rest":rest,"gw":gw,"accountId":f"# {index+1}","username":username,"rawToken":token}
    except Exception as e:
        L_error("",f"Login failed → {short}: {e}")
        gw.destroy(); return None

def _process_quests(account,questIds,counters):
    short=account["rawToken"][:20]+"..."; rest=account["rest"]; accId=account["accountId"]
    try:
        try: resp=rest.get("/quests/@me")
        except Exception as e:
            L_error("",f"fetchQuests failed → {short}: {e}")
            with _counter_lock: counters["failed"]+=1
            return
        qm=QuestManager.fromResponse(rest,resp)
        valid=qm.filterQuestsValid(questIds)
        alreadyClaimed=[q for q in qm.list() if q.hasClaimedRewards() and (len(questIds)==0 or q.id in questIds)]
        if alreadyClaimed:
            L_warning("",f"Already claimed → {short}")
            with _counter_lock: counters["success"]+=1
            _save_success(account["rawToken"]); return
        if not valid:
            L_error("",f"No valid quests → {short}")
            with _counter_lock: counters["failed"]+=1; return
        for q in valid:
            try: qm.doingQuest(q,accId); break
            except Exception as e:
                if getattr(e,"status",0)==404: continue
                L_error("",f"Quest error → {short}: {e}"); break
        with _counter_lock: counters["success"]+=1
        _save_success(account["rawToken"])
    except Exception as e:
        L_error("",f"Failed → {short}: {e}")
        with _counter_lock: counters["failed"]+=1
    finally:
        try: account["gw"].destroy()
        except: pass

def run_bot(quest_ids=None,max_threads=5):
    qIds=quest_ids or []
    tokens=_load_tokens_from_file()
    if not tokens: L_error("","No valid tokens found"); return
    L_info("",f"Quest Completer → {len(tokens)} tokens | threads: {max_threads}")
    counters={"success":0,"failed":0}
    totalBatches=-(-len(tokens)//max_threads)
    for b in range(totalBatches):
        start=b*max_threads; end=min(start+max_threads,len(tokens)); batch=tokens[start:end]
        accounts=[]
        with ThreadPoolExecutor(max_workers=max(1,len(batch))) as ex:
            futs={ex.submit(_login_account,t,start+i):t for i,t in enumerate(batch)}
            for f in as_completed(futs):
                try:
                    acc=f.result()
                    if acc: accounts.append(acc)
                except: pass
        if not accounts: continue
        with ThreadPoolExecutor(max_workers=max(1,len(accounts))) as ex:
            futs=[ex.submit(_process_quests,acc,qIds,counters) for acc in accounts]
            for f in as_completed(futs):
                try: f.result()
                except: pass
    L_info("",f"Completer done → ✓ {counters['success']}  ✗ {counters['failed']}")

def run_quest_completer(cfg):
    qIds=[q for q in cfg.get("quest_ids",[]) if q and q.strip()]
    threads=int(cfg.get("threads",5)); enroll_first=cfg.get("enroll_first",True)
    if enroll_first:
        L_info("","Enroll phase...")
        discovered=run_enroll(qIds,max_threads=threads)
        if not qIds and discovered: qIds=discovered
    run_bot(quest_ids=qIds,max_threads=threads)
    return qIds

# ═══════════════════════════════════════════════════════
# MAIN PROGRAM HELPERS
# ═══════════════════════════════════════════════════════

def load_config():
    try:
        with open(CONFIG_FILE) as f: return json.load(f)
    except: return {}

def load_tokens_from_env():
    tokens=[]
    for key,val in sorted(os.environ.items()):
        if key.startswith("DISCORD_TOKEN_") and val.strip(): tokens.append(val.strip())
    if tokens:
        with open(TOKENS_FILE,"w",encoding="utf-8") as f: f.write("\n".join(tokens)+"\n")
        log_ok(f"Loaded {len(tokens)} token(s) from DISCORD_TOKEN_* env vars")
    return tokens

def resolve_invite(code):
    code=code.strip().replace("https://discord.gg/","").replace("discord.gg/","").split("/")[-1].split("?")[0]
    try:
        r=requests.get(f"https://discord.com/api/v10/invites/{code}?with_counts=true",headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code==200:
            d=r.json()
            return {"guild_id":d["guild_id"],"invite_code":code,"guild_name":d.get("guild",{}).get("name","?")}
    except: pass
    return None

def get_headers(token):
    global _hdr_cache,_hdr_time
    now=time.time()
    if _hdr_cache and now-_hdr_time<300: return _hdr_cache
    sup=base64.b64encode(json.dumps({"os":"Windows","browser":"Discord Client","release_channel":"stable","client_version":"1.0.9215","os_version":"10.0.19045","os_arch":"x64","system_locale":"en-US","has_client_mods":False},separators=(',',':')).encode()).decode()
    hdrs={"Authorization":token,"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36","X-Super-Properties":sup,"Origin":"https://discord.com","Referer":"https://discord.com/channels/@me"}
    _hdr_cache=hdrs; _hdr_time=now; return hdrs

async def verify_token(token):
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://discord.com/api/v10/users/@me",headers=get_headers(token)) as r:
            if r.status==200:
                d=await r.json(); return (d.get("username","?"),d.get("discriminator","0"))
    return None

async def check_membership(token,guild_id):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://discord.com/api/v10/users/@me/guilds",headers=get_headers(token)) as r:
            if r.status==200:
                guilds=await r.json(); return any(g.get("id")==guild_id for g in guilds)
    return False

async def join_via_invite(token,invite_code):
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f"https://discord.com/api/v10/invites/{invite_code}",headers=get_headers(token),json={}) as r:
            return r.status in (200,201,204)

async def join_via_oauth2(bot_token,guild_id,user_id,access_token):
    async with aiohttp.ClientSession() as sess:
        h=get_headers(bot_token)
        async with sess.put(f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}",headers=h,json={"access_token":access_token}) as r:
            return r.status in (200,201,204)

def oauth_authorize(token,cfg):
    client_id=cfg.get("client_id"); client_secret=cfg.get("client_secret"); redirect_uri=cfg.get("redirect_uri","http://localhost:8080")
    if not client_id or not client_secret: return None
    try:
        sess=Session(client_identifier="chrome_120")
        sup=base64.b64encode(json.dumps({"os":"Windows","browser":"Discord Client","release_channel":"stable","client_version":"1.0.9215"},separators=(',',':')).encode()).decode()
        hdrs={"Authorization":token,"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)","X-Super-Properties":sup,"Origin":"https://discord.com","Referer":"https://discord.com/channels/@me"}
        r=sess.get("https://discord.com/api/v10/users/@me",headers=hdrs)
        if r.status_code!=200: return None
        uid=r.json()["id"]
        o=sess.post("https://discord.com/api/v10/oauth2/authorize",headers=hdrs,json={"authorization_details":[{"type":2,"application_id":client_id,"location":"guild_join","location_context":{}}],"permissions":"0","authorize":True,"integration_type":0})
        if o.status_code==200:
            jo=o.json(); loc=jo.get("location","")
            if "code=" in loc:
                code=loc.split("code=")[1].split("&")[0]
                t=sess.post("https://discord.com/api/v10/oauth2/token",headers={"Content-Type":"application/x-www-form-urlencoded"},data=f"client_id={client_id}&client_secret={client_secret}&grant_type=authorization_code&code={code}&redirect_uri={redirect_uri}")
                if t.status_code==200: return (uid,t.json().get("access_token"),token)
        return None
    except: return None

async def vc_connect(token,guild_id,channel_id,mute,video,stream,index,stop_event):
    tag=f"[VC#{index+1}]"
    ws_url="wss://gateway.discord.gg/?v=10&encoding=json"
    while not stop_event.is_set():
        try:
            async with websockets.connect(ws_url,max_size=None) as ws:
                data=json.loads(await ws.recv())
                if data["op"]!=10: continue
                hb_int=data["d"]["heartbeat_interval"]/1000
                async def hb():
                    while not stop_event.is_set():
                        await ws.send(json.dumps({"op":1,"d":None})); await asyncio.sleep(hb_int)
                asyncio.create_task(hb())
                await ws.send(json.dumps({"op":2,"d":{"token":token,"capabilities":30717,"properties":{"os":"Windows","browser":"Discord Client","release_channel":"stable","client_version":"1.0.9215","os_version":"10.0.19045","os_arch":"x64","system_locale":"en-US","has_client_mods":False,"browser_user_agent":"Mozilla/5.0","browser_version":"37.6.0","client_build_number":471091,"native_build_number":72186},"presence":{"status":"online","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{}}}}))
                async for raw in ws:
                    p=json.loads(raw)
                    if p.get("t")=="READY": break
                await ws.send(json.dumps({"op":4,"d":{"guild_id":guild_id,"channel_id":channel_id,"self_mute":mute,"self_deaf":False,"self_video":video,"flags":(2 if stream else 0)}}))
                log_ok(f"{tag} connected to VC")
                await asyncio.sleep(300); await ws.close()
        except Exception as e:
            if not stop_event.is_set():
                log_warn(f"{tag} VC error: {e}, reconnecting in 10s..."); await asyncio.sleep(10)

async def fetch_messages(token,channel_id,limit=10):
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}",headers=get_headers(token)) as r:
            if r.status==200: return await r.json()
    return []

async def send_msg(token,channel_id,content):
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f"https://discord.com/api/v10/channels/{channel_id}/messages",headers=get_headers(token),json={"content":content}) as r:
            if r.status in(200,201): return True,await r.json()
            return False,None

async def trigger_typing(token,channel_id):
    async with aiohttp.ClientSession() as sess:
        async with sess.post(f"https://discord.com/api/v10/channels/{channel_id}/typing",headers=get_headers(token)) as r:
            return r.status==204

async def start_chat_loop(tokens,channel_id,delay,smart_mode,stop_event):
    log_info("Chat automation starting...")
    from conversation import SmartChatBot
    bots=[SmartChatBot() for _ in tokens]; msg_idx=0
    while not stop_event.is_set():
        for i,(token,bot) in enumerate(zip(tokens,bots)):
            if stop_event.is_set(): break
            tag=f"[CHAT#{i+1}]"
            try:
                msgs=await fetch_messages(token,channel_id)
                last_msg=msgs[0]["content"] if msgs else None
                is_starter=msg_idx==0 or random.random()<0.3
                msg_content=bot.get_message(last_msg,is_starter)
                log_info(f"{tag} typing..."); await trigger_typing(token,channel_id)
                await asyncio.sleep(len(msg_content)*0.05+0.3)
                success,_=await send_msg(token,channel_id,msg_content)
                if success: log_ok(f"{tag} sent: {msg_content[:60]}")
                else: log_warn(f"{tag} failed to send")
                msg_idx+=1; await asyncio.sleep(delay+random.uniform(0.5,2.0))
            except Exception as e: log_warn(f"{tag} error: {e}"); await asyncio.sleep(5)

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

async def main():
    show_banner()
    tokens=load_tokens_from_env()
    if not tokens: log_fail("No tokens. Set DISCORD_TOKEN_1..N in Railway vars."); sys.exit(1)
    cfg=load_config()
    cfg["bot_token"]=os.environ.get("BOT_TOKEN",cfg.get("bot_token",""))
    cfg["client_id"]=os.environ.get("CLIENT_ID",cfg.get("client_id",""))
    cfg["client_secret"]=os.environ.get("CLIENT_SECRET",cfg.get("client_secret",""))
    log_info(f"Verifying {len(tokens)} tokens...")
    info=await verify_token(tokens[0])
    if info is None: log_fail("Auth failed. Check DISCORD_TOKEN_1."); sys.exit(1)
    uname,disc=info; spin_result(f"CONNECTED · {uname}#{disc} · {len(tokens)} token(s)",MINT)
    box("INITIALIZATION",EMBER)
    ic=INVITE_CODE; gid=GUILD_ID
    if ic and not gid:
        ri=resolve_invite(ic)
        if ri: gid=ri["guild_id"]; ic=ri["invite_code"]; log_ok(f"Guild: {ri['guild_name']} ({gid})")
        else: log_fail(f"Bad invite: {ic}"); sys.exit(1)
    elif gid: log_ok(f"Using Guild ID: {gid}")
    else: log_fail("Set INVITE_CODE env var"); sys.exit(1)
    vc_id=VC_CHANNEL_ID if ENABLE_VC else ""
    text_id=TEXT_CHANNEL_ID if ENABLE_CHAT else ""
    if not vc_id and not text_id and not ENABLE_QUESTS: log_fail("No channels. Set ENABLE_VC or ENABLE_CHAT."); sys.exit(1)
    mute_c=MUTE_COUNT if MUTE_COUNT>0 else len(tokens) if vc_id else 0
    vid_c=VIDEO_COUNT; str_c=STREAM_COUNT; delay=CHAT_DELAY; smart_opt=SMART_CHAT
    divider()
    if ENABLE_QUESTS:
        qc=cfg.get("quest_completer",{})
        if qc.get("enabled",True):
            box("QUEST COMPLETER",MINT)
            log_info("Running Quest Completer...")
            completed=run_quest_completer(qc)
            log_ok(f"Quest Completer: {len(completed)} quest(s)"); divider()
    box("AUTHORIZATION",EMBER)
    log_info("Authorizing via OAuth...")
    authed=[]
    with ThreadPoolExecutor(max_workers=cfg.get("max_workers",10)) as ex:
        futs=[ex.submit(oauth_authorize,t,cfg) for t in tokens]
        for f in as_completed(futs):
            res=f.result()
            if res: authed.append(res)
    log_ok(f"Authorized: {len(authed)}/{len(tokens)}")
    box("MEMBERSHIP",LAVA)
    bt=cfg.get("bot_token"); joined=0
    log_info("Joining server...")
    for uid,at,tk in authed:
        ig=await check_membership(tk,gid)
        if not ig:
            success=False
            if bt and bt.startswith("MT"): success=await join_via_oauth2(bt,gid,uid,at)
            if not success and ic: success=await join_via_invite(tk,ic)
            if success: joined+=1
            else: log_fail(f"Token {tk[:15]}... failed")
        else: joined+=1
    log_ok(f"In server: {joined}/{len(authed)}")
    if joined==0: log_fail("No tokens joined"); sys.exit(1)
    box("DEPLOYMENT",GOLD); log_info("Starting deployment...")
    stop_event=asyncio.Event(); tasks=[]
    if vc_id:
        log_info("Spawning VC joiners...")
        for i,a in enumerate(authed):
            mute=i<mute_c; video=mute_c<=i<(mute_c+vid_c); stream=(mute_c+vid_c)<=i<(mute_c+vid_c+str_c)
            tasks.append(asyncio.create_task(vc_connect(a[2],gid,vc_id,mute,video,stream,i,stop_event)))
            await asyncio.sleep(0.3)
    if text_id:
        log_info("Spawning chat...")
        ct=[a[2] for a in authed]; tasks.append(asyncio.create_task(start_chat_loop(ct,text_id,delay,smart_opt,stop_event)))
    log_ok("Running! Ctrl+C to stop.\n")
    try: await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt): log_warn("Shutting down...")
    finally: stop_event.set(); [t.cancel() for t in tasks]; log_ok("Stopped.")

def show_banner():
    print(c(0,200,255)+B+r"""
   ██╗  ██╗██╗███╗   ██╗███████╗██╗  ██╗ ██████╗ 
   ██║  ██║██║████╗  ██║██╔════╝██║  ██║██╔═══██╗
   ███████║██║██╔██╗ ██║███████╗███████║██║   ██║
   ╚══██╔══╝██║██║╚██╗██║╚════██║██╔══██║██║   ██║
      ██║   ██║██║ ╚████║███████║██║  ██║╚██████╔╝
      ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ 
    """+R)
    print(f"          {B}{c(0,255,120)}developer WINSHO{R}\n")

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: log_warn("Exited.")
    except Exception as e: log_fail(f"Fatal: {e}"); traceback.print_exc()
