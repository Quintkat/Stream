from Thought import Thought
import json
from datetime import datetime
from os import listdir


class Stream:
	startID : int
	name : str
	thoughts : dict[int, Thought]

	def __init__(self, name):
		self.thoughts = {}
		self.startID = 0
		self.name = name

	def addThought(self, thought : Thought):
		if thought.id() not in self.thoughts:
			self.thoughts[thought.id()] = thought

	def removeThought(self, ID : int):
		if ID in self.thoughts:
			thought = self.getThought(ID)
			for rel in thought.related():
				rel.removeOffspring(ID)
			del self.thoughts[ID]

	def getThought(self, ID) -> Thought:
		if ID in self.thoughts:
			return self.thoughts[ID]
		else:
			return None

	def getThoughts(self) -> dict[int, Thought]:
		return self.thoughts

	def getThoughtIndex(self, index) -> Thought:
		keys : list = list(self.thoughts.keys())
		if index >= len(keys):
			return None

		return self.thoughts[keys[index]]

	def newID(self) -> int:
		maxID : int = self.startID
		for k in self.thoughts.keys():
			if k > maxID:
				maxID = k

		return maxID + 1

	def saveFileName(self) -> str:
		return "saves/" + self.name + ".json"

	def loadFromJSON(self):
		loadDict : dict
		sf = self.saveFileName()

		with open(sf) as load:
			loadDict = json.load(load)

		# At this point, loadDict is structured as dict[str, dict]
		# The second dict has the saves to be turned into Thoughts and the string is the string version of the integer IDs
		for ID in loadDict:
			thoughtData = loadDict[ID]
			tID : int = thoughtData["id"]
			tTime : datetime = datetime.strptime(thoughtData["time"], "%Y-%m-%d %H:%M:%S.%f")
			tString : str = thoughtData["string"]
			thought = Thought(tID, tString, tTime)
			self.addThought(thought)

		# The relations need to be loaded second for the case that there are any thoughts that relate to thoughts not yet loaded.
		for ID in loadDict:
			thoughtData = loadDict[ID]
			tID : int = thoughtData["id"]
			thought = self.getThought(tID)
			for rID in thoughtData["related"]:
				thought.addRelated(self.getThought(rID))

	def saveToJSON(self):
		saveDict : dict = {}
		thoughts : dict = self.getThoughts()
		for ID in thoughts:
			thought : Thought = thoughts[ID]
			saveDict[ID] = thought.dataJSON()

		sf = self.saveFileName()
		with open(sf, 'w') as save:
			json.dump(saveDict, save, indent=4)


def getAllStreamNames() -> list[str]:
	streamNames = []
	for f in listdir("saves"):
		streamNames.append(f.split('.')[0])

	return streamNames
