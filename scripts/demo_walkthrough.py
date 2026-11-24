"""Run the offline walkthrough with a new SQLite database and fail on any missing step."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

import httpx

ROOT=Path(__file__).resolve().parents[1]
EXAMPLES=ROOT/"examples"


def check(condition,message):
    if not condition:
        raise RuntimeError(message)


def walkthrough(api):
    def request(method,path,**kwargs):
        response=api.request(method,"/api/v1"+path,**kwargs)
        if response.is_error:
            raise RuntimeError(f"{method} {path}: {response.status_code} {response.text}")
        return response.json()

    def upload(path,file,media=None):
        return request("POST",path,files={"file":(file.name,file.read_bytes(),media)})

    course=request("POST","/courses",json=json.loads((EXAMPLES/"course.json").read_text()))["id"]
    base="/courses/"+course
    groups=[]
    for file in ("saturday.ics","monday.csv"):
        preview=upload("/calendar/preview",EXAMPLES/"schedules"/file)
        check(len(preview["groups"])==1 and not preview["errors"],"Calendar preview")
        groups.append(request("POST",base+"/groups",json=preview["groups"][0])["id"])
    for file in sorted((EXAMPLES/"materials").iterdir()):
        m=upload(base+"/materials",file,"text/plain")
        check(m["status"]=="processed" and m["chunks"],"Located source missing")
    print("PASS · both schedules and three materials",flush=True)
    plan=request("POST",base+"/roadmaps/generate",headers={"Idempotency-Key":"walkthrough"})
    path="/roadmaps/"+plan["id"]
    check(all(s["supporting_chunk_ids"] for s in plan["sessions"]),"Missing citations")
    parent={t["id"]:t["stable_id"] for t in plan["topics"]}
    topics=[dict(t,id=t["stable_id"]) for t in plan["topics"]]
    sessions=[dict(s,id=s["stable_id"],topic_id=parent[s["topic_id"]]) for s in plan["sessions"]]
    edges=plan["session_edges"]
    next(e for e in edges if e["edge_type"]=="reinforces").update(edge_type="extends",note="Practice builds on loops")
    request("PUT",path,json=dict(topics=topics,sessions=sessions,session_edges=edges,warnings=plan["warnings"]))
    request("POST",path+"/approve")
    saved=request("GET",base+"/roadmaps/approved")
    check(len(edges)==3 and sorted(edges,key=str)==sorted(saved["session_edges"],key=str),"Links changed on reload")
    print("PASS · three typed session links survived edit, approval and GET",flush=True)
    session=saved["sessions"][0]["id"]
    group_paths=["/groups/"+key for key in groups]
    request("PUT",group_paths[0]+"/sessions/"+session+"/progress",json={"state":"completed"})
    for i,group in enumerate(group_paths):
        facts=request("GET",group+"/overview")
        check(facts["sessions"][0]["state"]==("completed" if i==0 else "upcoming"),"Progress leaked")
        check(any(r["missing_id"]=="functions" for r in facts["reminders"])==(i==1),"Prerequisite reminder mismatch")
    print("PASS · independent group progress and actionable reminder",flush=True)
    review=upload(group_paths[0]+"/sessions/"+session+"/reviews",EXAMPLES/"transcript.txt","text/plain")
    evidence=review["findings"][0]["evidence"][0]
    check(review["transcript"][evidence["start"]:evidence["end"]]==evidence["snippet"],"Invalid quoted evidence")
    rpath="/reviews/"+review["id"]
    request("PUT",rpath,json={"findings":review["findings"]})
    request("POST",rpath+"/approve")
    package=request("POST",rpath+"/package")
    for name,item in package["items"].items():
        package=request("PUT",f"/packages/{package['id']}/items/{name}",json={"text":item["text"],"approve":True})
    check(package["state"]=="approved" and not request("GET",base+"/approvals"),"Approval queue not cleared")
    print("PASS · cited findings, four individual approvals and empty queue",flush=True)
    result=request("POST",base+"/assistant",json={"group_id":groups[0],"question":"What is a loop?"})
    check(result["status"]=="answered" and "loop repeats" in result["answer"] and "loops.txt" in result["references"][0]["label"],"Missing grounded answer")
    check(request("GET",base+"/history")[-1]["state"]=="approved","Missing approval history")
    print("PASS · cited assistant response and local approval history",flush=True)
    return course


def run(port,serve,empty=False,browser_check=False):
    if port==0:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1",0))
            port=sock.getsockname()[1]
    with tempfile.TemporaryDirectory() as temp:
        env=dict(os.environ,TEACHFLOW_DATA_DIR=temp,DATABASE_URL="sqlite:///"+Path(temp,"demo.db").as_posix(),
                 LLM_API_KEY="",PYTHONPATH=os.pathsep.join([str(ROOT/"backend"),str(ROOT/"scripts")]))
        subprocess.run([sys.executable,"-m","alembic","upgrade","head"],cwd=ROOT/"backend",env=env,check=True)
        server=subprocess.Popen([sys.executable,"-m","uvicorn","fixture_app:app","--host","127.0.0.1","--port",str(port),"--log-level","warning"],
                                env=env,cwd=ROOT/"backend")
        url=f"http://127.0.0.1:{port}"
        try:
            with httpx.Client(base_url=url,trust_env=False,timeout=10) as api:
                for _ in range(120):
                    if server.poll() is not None:
                        raise RuntimeError("Demo server exited. Check the port.")
                    try:
                        health=api.get("/health/ready")
                        if health.is_success and health.headers.get("X-TeachFlow-Demo")=="recorded":
                            break
                    except httpx.ConnectError:
                        pass
                    time.sleep(.1)
                else:
                    raise RuntimeError("The isolated fixture server did not become ready.")
                if not empty:
                    course=walkthrough(api)
                    if browser_check:
                        from demo_browser import verify
                        verify(url,course)
                if serve:
                    print(f"Recorded synthetic demo at {url}. Press Ctrl+C to close it.",flush=True)
                    server.wait()
        except KeyboardInterrupt:
            pass
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--serve",action="store_true",help="Keep the disposable app open after verification")
    parser.add_argument("--empty",action="store_true",help="Start with a clean form for the manual checklist")
    parser.add_argument("--port",type=int,default=8000,help="Use 0 for a free local port")
    parser.add_argument("--browser",action="store_true",help="Also exercise instructor screens with Playwright")
    args=parser.parse_args()
    run(args.port,args.serve,args.empty,args.browser)
