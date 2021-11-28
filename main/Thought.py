from __future__ import annotations
from datetime import datetime
from typing import List, TypedDict


class Data(TypedDict):
	id : int
	time : datetime
	string : str
	related : List[Thought]
	offspring : List[Thought]


class Thought:
	data : Data

	def __init__(self, ID, string, time : datetime = None, related : list[Thought] = None):
		self.data = {"id" : 0, "time" : datetime(2000, 1, 1), "string" : "", "related" : [], "offspring" : []}
		self.setID(ID)
		self.setText(string)

		if time is None:
			self.setTime(datetime.now())
		else:
			self.setTime(time)

		if related is not None:
			self.setRelated(related)

	def setID(self, ID : int):
		self.data["id"] = ID

	def id(self) -> int:
		return self.data["id"]

	def setTime(self, time : datetime):
		self.data["time"] = time

	def time(self) -> datetime:
		return self.data["time"]

	def timeStr(self) -> str:
		time = self.time()
		return self.timeStrTime() + " " + self.timeStrDate()

	def timeStrDate(self) -> str:
		time = self.time()
		return time.strftime("%d-%m-%y")

	def timeStrTime(self) -> str:
		time = self.time()
		return time.strftime("%I:%M %p")

	def setText(self, string : str):
		self.data["string"] = string

	def text(self) -> str:
		return self.data["string"]

	def setRelated(self, related : List[Thought]):
		self.data["related"] = related

	def addRelated(self, related : Thought):
		if related not in self.data["related"] and related.id != self.id():
			self.data["related"].append(related)
			related.addOffspring(self)

	def addRelatedList(self, related : List[Thought]):
		for r in related:
			self.addRelated(r)

	def removeRelated(self, related : Thought):
		if related in self.data["related"]:
			related.removeOffspring(self.id())
			self.data["related"].remove(related)

	def removeRelatedList(self, related: List[Thought]):
		for rel in related:
			self.removeRelated(rel)

	def related(self) -> List[Thought]:
		return self.data["related"]

	def setOffspring(self, offspring : List[Thought]):
		self.data["offspring"] = offspring

	def addOffspring(self, offspring : Thought):
		if offspring not in self.data["offspring"]:
			self.data["offspring"].append(offspring)

	def addOffspringList(self, offspring : List[Thought]):
		for o in offspring:
			self.addOffspring(o)

	def removeOffspring(self, ID : int):
		for o in range(len(self.offspring())):
			offspring = self.offspring()[o]
			if offspring.id() == ID:
				self.setOffspring(self.offspring()[0:o] + self.offspring()[o + 1 : -1])


	def offspring(self) -> List[Thought]:
		return self.data["offspring"]

	def strIDDatetime(self):
		return "Thought " + str(self.id()) + " at " + self.timeStr()

	def __str__(self):
		output = self.strIDDatetime()+ ": " + self.text()
		if len(self.related()) > 0:
			output += "; Related to thoughts "
			output += str(self.related()[0].id())
			for r in self.related()[1:]:
				output += ", " + str(r.id())
		return output

	def dataAll(self) -> Data:
		return self.data

	def dataJSON(self) -> dict:
		newData : dict = {}
		newData["id"] = self.id()
		newData["time"] = str(self.time())
		newData["string"] = self.text()

		rel = self.related()
		newData["related"] = []
		for r in rel:
			newData["related"].append(r.id())

		# off = self.offspring()
		# newData["offspring"] = []
		# for o in off:
		# 	newData["offspring"].append(o.id())

		return newData

