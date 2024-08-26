import os
import sys
import time
import hashlib
import threading

import uvicorn
from fastapi import FastAPI, Request, Response, status, Body

from petdb import PetDB, PetCollection, PetArray
from petdb.service.api import DEFAULT_PORT
from petdb.service.qlock import QLock

if sys.platform != "linux":
	raise Exception("PetDB.service supports only Linux system")

STORAGE_PATH = "/var/lib/petdb"
if not os.path.exists(STORAGE_PATH):
	os.makedirs(STORAGE_PATH, exist_ok=True)

db = PetDB.get(STORAGE_PATH)
app = FastAPI()
lock = QLock()

@app.post("/collections")
def get_collections():
	with lock:
		return db.collections()

@app.post("/drop")
def drop_collections():
	with lock:
		db.drop()

@app.post("/drop/{name}")
def drop_collection(name: str):
	with lock:
		db.drop_collection(name)

@app.post("/mutate/{name}")
def mutate(name: str, mutations: list[dict] = Body(embed=True)):
	with lock:
		array = db.collection(name)
		for mutation in mutations:
			array: PetArray = array.__getattribute__(mutation["type"])(*mutation["args"])
		return array.list()

@app.post("/insert/{name}")
def insert(name: str, doc: dict = Body(embed=True)):
	with lock:
		return db.collection(name).insert(doc)

@app.post("/insert_many/{name}")
def insert_many(name: str, docs: list[dict] = Body(embed=True)):
	with lock:
		return db.collection(name).insert_many(docs)

@app.post("/update_one/{name}")
def update_one(name: str, update: dict = Body(embed=True), query: dict = Body(embed=True)):
	with lock:
		return db.collection(name).update_one(update, query)

@app.post("/update/{name}")
def update(name: str, update: dict = Body(embed=True), query: dict = Body(embed=True)):
	with lock:
		return db.collection(name).update(update, query)

@app.post("/remove/{name}")
def remove(name: str, query: dict = Body(embed=True)):
	with lock:
		return db.collection(name).remove(query)

@app.post("/clear/{name}")
def clear(name: str):
	with lock:
		return db.collection(name).clear()

def cache_monitor():
	while True:
		print("start cache checking...")
		now = int(time.time())
		with lock:
			instances = PetCollection.instances()
			for path in list(instances.keys()):
				print(f"check {instances[path]["instance"].name}...")
				if now - instances[path]["created"] > 3 * 24 * 3600:
					print(f"clear {instances[path]["instance"].name}")
					del instances[path]
		time.sleep(24 * 3600)

def run(port: int = DEFAULT_PORT, password_hash: str = ""):

	@app.middleware("http")
	async def authentication(request: Request, call_next):
		body = await request.json()
		if hashlib.sha256(body["password"].encode("utf-8")).hexdigest() == password_hash:
			return await call_next(request)
		return Response(status_code=status.HTTP_401_UNAUTHORIZED)

	threading.Thread(target=cache_monitor).start()

	uvicorn.run(app, host="127.0.0.1", port=port)
