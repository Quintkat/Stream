from tkinter import *
from tkinter import ttk
from math import floor, log

from Thought import Thought
from Stream import Stream, getAllStreamNames


class MainWindow(Tk):
	# Default settings
	wWidth = 1040
	wHeight = 605
	wOffsetX = 450
	wOffsetY = 200
	wTitle = "Stream"

	# Style settings
	cText = "black"
	cGhostText = "grey"
	style : dict = {
			"cText" : "#CFCFCF",
			"cGhostText" : "#757575",
			"cLabelframeBorder" : "#424242",
			"cbg1" : "#212121",
			"cbg2" : "#424242",
			"cbg3" : "#616161",
			"cbg4" : "#757575",
			"borderFlush" : 0,
			"border" : 1,
			"fText" : ("Helvetica", 9),
			"fTextLarge" : ("Calibri", 12),
	}

	# GUI elements
	padX = 5
	padY = 5
	frameTable : Frame
	entryThought : Entry
	tableStream : ttk.Treeview
	frameThought : LabelFrame
	textThought : Text
	buttonDelete : Button
	checkRelated : Checkbutton
	frameStream : LabelFrame
	entryStream : Entry
	labelStream : Label
	optionStream : OptionMenu
	buttonStream : Button
	buttonRelatedShow : Button
	buttonRelatedAdd : Button
	buttonRelatedRemove : Button
	buttonOffspringShow : Button
	labelThought : Label

	# Stream vars
	optionStreamVal : StringVar

	# TableStream vars
	tableStreamColumns : list[str] = ["date", "time", "thought"]
	maxTableID : int = 0

	# Stream saves
	stream : Stream
	streamDefault : str = "default"
	streamNameList : list[str]

	# CheckRelated vars
	checkRelatedVal : IntVar

	# Thought frame vars
	displayIDNone : int = -1
	displayID : int = displayIDNone
	addingRelated : bool = False
	removingRelated : bool = False
	addRelatedText = {False : "Add related", True : "Add selection"}
	removeRelatedText = {False : "Remove related", True : "Remove selection"}
	labelThoughtVal : StringVar
	noThoughtSelected : str = "No thought selected"

	def __init__(self):
		super().__init__()
		self.windowSetup()
		self.environmentSetup()
		self.mainloop()


	def windowSetup(self):
		self.title(self.wTitle)
		self.iconbitmap("stream.ico")
		self.geometry(str(self.wWidth) + "x" + str(self.wHeight) + "+" + str(self.wOffsetX) + "+" + str(self.wOffsetY))


	def environmentSetup(self):
		self.streamSetup()
		self.frameStreamSetup()
		self.frameThoughtSetup()
		self.frameTableSetup()
		self.styleSetup()
		self.afterStyleSetup()


	def streamSetup(self):
		self.stream = Stream(self.streamDefault)
		self.stream.loadFromJSON()

	def switchStream(self, name : str, updateTable : bool = True):
		self.stream.saveToJSON()
		self.stream = Stream(name)
		self.stream.loadFromJSON()
		if updateTable:
			self.updateTable()


	def frameStreamSetup(self):
		frame = LabelFrame(self, text="Stream")
		self.frameStream = frame
		frame.grid(column=0, row=1, padx=self.padX, pady=self.padY, sticky='ewn')
		# frame.pack(side="top")

		self.entryStreamSetup()
		self.labelStreamSetup()
		self.optionStreamSetup()
		self.buttonStreamSetup()

	def entryStreamSetup(self):
		entry = Entry(self.frameStream, exportselection=0, width=30)
		self.entryStream = entry
		entry.grid(column=0, row=0, columnspan=2, padx=self.padX, pady=self.padY, sticky='ew')
		entry.bind("<FocusIn>", self.entryStreamFocusIn)
		entry.bind("<FocusOut>", self.entryStreamFocusOut)
		entry.bind("<Return>", self.entryCreateStream)

	def entryStreamFocusIn(self, a):
		print("lk")
		if self.entryStream["fg"] == self.style["cGhostText"]:
			self.entryStream.delete(0, END)
			self.entryStream.config(fg=self.style["cText"])

	def entryStreamFocusOut(self, a):
		text = self.entryStream.get()
		if text == "":
			self.entryStream.delete(0, END)
			self.entryStream["fg"] = self.style["cGhostText"]
			self.entryStream.insert(0, "New Stream")

	def entryCreateStream(self, a):
		newName = self.entryStream.get()
		if newName == "":
			return

		newStream = Stream(newName)
		newStream.saveToJSON()
		self.updateStreamNameList()
		self.updateOptionStream(newName)
		self.switchStream(newName)
		self.styleSetup()

	def labelStreamSetup(self):
		label = Label(self.frameStream, text="Current Stream:")
		self.labelStream = label
		label.grid(column=0, row=1, sticky="w", padx=self.padX, pady=self.padY)

	def optionStreamSetup(self, standardSelection : str = ""):
		self.updateStreamNameList()
		self.optionStreamVal = StringVar()
		if standardSelection == "":
			self.optionStreamVal.set(self.streamDefault)
		else:
			print(standardSelection)
			self.optionStreamVal.set(standardSelection)

		option = OptionMenu(self.frameStream, self.optionStreamVal, *self.streamNameList, command=self.displayStreamOption)
		self.optionStream = option
		option.grid(column=1, row=1, padx=self.padX, pady=self.padY)
		option.config(width=10)

	def updateStreamNameList(self):
		self.streamNameList = getAllStreamNames()

	def updateOptionStream(self, name : str = ""):
		self.optionStream.destroy()
		self.optionStreamSetup(name)

	def displayStreamOption(self, a):
		streamName = self.optionStreamVal.get()
		self.switchStream(streamName)

	def buttonStreamSetup(self):
		button = Button(self.frameStream, text="Refresh Stream", command=self.buttonStreamRefresh)
		self.buttonStream = button
		button.grid(column=0, row=2, columnspan=2, sticky="ew", padx=2*self.padX, pady=self.padY)

	def buttonStreamRefresh(self):
		self.updateTable()


	def frameTableSetup(self):
		frame = Frame(self)
		self.frameTable = frame
		frame.grid(column=1, row=1, padx=self.padX, pady=self.padY, rowspan=2)
		# frame.pack(side="right", fill='x')

		self.tableSetup()
		self.entryThoughtSetup()
		self.relatedSetup()

	def tableSetup(self):
		table = ttk.Treeview(self.frameTable)
		self.tableStream = table

		# Columns
		table["columns"] = self.tableStreamColumns
		table.column("#0", anchor=W, width=50, minwidth=50)
		table.column("date", anchor=CENTER, width=60, minwidth=60)
		table.column("time", anchor=CENTER, width=60, minwidth=60)
		table.column("thought", anchor=W, width=600, minwidth=500)

		# Headings
		table.heading("#0", text="#")
		table.heading("date", text="Date")
		table.heading("time", text="Time")
		table.heading("thought", text="Thought")

		# Data
		self.updateTable()

		# Positioning
		table.grid(column=0, row=0, padx=self.padX, pady=0, columnspan=2)

		# Binding
		table.bind("<ButtonRelease-1>", self.tableButtonRelease)

		# Settings
		# table["selectmode"] = "browse"
		table["height"] = 27

	def updateTable(self, query : list[int] = None):
		table = self.tableStream
		for item in table.get_children():
			table.delete(item)

		thoughts : dict[int, Thought] = {}
		if query is None:
			thoughts = self.stream.getThoughts()
		else:
			for ID in query:
				thoughts[ID] = self.stream.getThought(ID)

		for tID in thoughts:
			thought = thoughts[tID]
			info = (thought.timeStrDate(), thought.timeStrTime(), thought.text())
			table.insert(parent='', index='end', iid=tID, text=str(tID), values=info)

		if len(thoughts) > 0:
			self.maxTableID = max(thoughts)
			for tID in thoughts:
				thought = thoughts[tID]
				offspring = thought.offspring()
				# print(tID, offspring)
				for off in offspring:
					info = (off.timeStrDate(), off.timeStrTime(), off.text())
					table.insert(parent=str(tID), index='end', iid=self.idOGToChild(off.id(), tID), text=str(off.id()), values=info)

	def updateTableSingle(self, thoughtID):
		if len(self.stream.getThought(thoughtID).related()) > 0:
			self.updateTable()
		else:
			thought = self.stream.getThought(thoughtID)
			info = (thought.timeStrDate(), thought.timeStrTime(), thought.text())
			self.tableStream.insert(parent='', index='end', iid=thought.id(), text=str(thought.id()), values=info)

	def idOGToChild(self, cID : int, pID : int) -> int:
		OOM = floor(log(self.maxTableID, 10))
		return pID*pow(10, OOM + 3) + cID

	def idChildToOG(self, cID : int, pID : int) -> int:
		OOM = floor(log(self.maxTableID, 10))
		return cID - pID*pow(10, OOM + 3)

	def tableButtonRelease(self, a):
		if self.addingRelated:
			# self.manipulateRelated()
			pass
		elif self.removingRelated:
			# self.manipulateRelated()
			pass
		else:
			self.updateTextThought(0)

	def getSelectedIDs(self) -> list[int]:
		s = []
		for i in self.tableStream.selection():
			ID = int(i)
			if self.tableStream.parent(ID) != '':
				s.append(self.idChildToOG(ID, int(self.tableStream.parent(ID))))
			else:
				s.append(ID)
		return s

	def entryThoughtSetup(self):
		entry = Entry(self.frameTable, exportselection=0, width=106)
		entry.grid(column=0, row=1, sticky='w', padx=self.padX, pady=self.padY)
		entry.bind("<Return>", self.entryCreateThought)
		self.entryThought = entry

	def entryCreateThought(self, a):
		# Create the thought
		text = self.entryThought.get()
		related = None
		if self.checkRelatedVal.get() == 1:
			related = []
			for ID in self.getSelectedIDs():
				related.append(self.stream.getThought(ID))

		thought = Thought(self.stream.newID(), text, related=related)

		# Add to stream
		self.stream.addThought(thought)
		self.stream.saveToJSON()

		# Update the table
		self.updateTableSingle(thought.id())
		self.entryThought.delete(0, END)

	def relatedSetup(self):
		self.checkRelatedVal = IntVar()
		check = Checkbutton(self.frameTable, text="Related to selection", variable=self.checkRelatedVal)
		self.checkRelated = check
		check.grid(column=1, row=1, sticky='e')


	def frameThoughtSetup(self):
		frame = LabelFrame(self, text="Thought")
		self.frameThought = frame
		frame.grid(column=0, row=2, padx=self.padX, pady=self.padY, sticky='ns')
		# frame.pack(side="bottom", expand=True)

		self.textThoughtSetup()
		self.buttonDeleteSetup()
		self.buttonRelatedShowSetup()
		self.buttonRelatedAddSetup()
		self.buttonRelatedRemoveSetup()
		self.labelThoughtSetup()

	def textThoughtSetup(self):
		text = Text(self.frameThought, width=25, padx=2, height=16)
		self.textThought = text
		text.grid(column=0, row=3, columnspan=2, sticky='ns', padx=self.padX, pady=self.padY)
		text.insert(END, "uwu")
		text.bind("<Return>", self.textThoughtUpdate)
		text.bind("<KeyRelease-Return>", self.textThoughtAfterEnter)

	def updateTextThought(self, a):
		print("weawew")
		selection = self.getSelectedIDs()

		if len(selection) == 1:
			self.textThought.delete(1.0, END)
			self.displayID = int(selection[0])
			thought : Thought = self.stream.getThought(self.displayID)
			self.textThought.insert(1.0, thought.text())

			# Update label
			self.labelThoughtVal.set(thought.strIDDatetime())

	def textThoughtUpdate(self, a):
		if self.displayID != self.displayIDNone:
			ID = self.displayID
			thought : Thought = self.stream.getThought(ID)
			thought.setText(self.textThought.get(1.0, 'end-1c'))		# Edit the thought (have to keep the trailing \n in mind)
			self.stream.saveToJSON()									# Save the stream
			self.updateTable()											# Update the entire table
			self.textThought.delete(1.0, END)							# Re-update the text with the updated text
			self.textThought.insert(1.0, thought.text())

	def textThoughtAfterEnter(self, a):
		self.textThought.delete('end-1c', END)


	def buttonDeleteSetup(self):
		button = Button(self.frameThought, text="Delete Thought", command=self.deleteThought)
		self.buttonDelete = button
		button.grid(column=0, row=4, columnspan=2, sticky='ews', padx=2*self.padX, pady=self.padY)

	def deleteThought(self):
		selection = self.getSelectedIDs()
		if len(selection) == 0:
			return

		for sID in selection:
			self.stream.removeThought(sID)

		self.stream.saveToJSON()
		self.updateTable()

	def labelThoughtSetup(self):
		self.labelThoughtVal = StringVar()
		self.labelThoughtVal.set(self.noThoughtSelected)
		label = Label(self.frameThought, textvariable=self.labelThoughtVal, anchor='w')
		self.labelThought = label
		label.grid(column=0, row=2, columnspan=2, sticky='ew', padx=self.padX, pady=self.padY)

	def buttonRelatedShowSetup(self):
		button = Button(self.frameThought, text="Show related", command=self.showRelated)
		self.buttonRelatedShow = button
		button.grid(column=0, row=0, columnspan=2, sticky='ew', padx=self.padX, pady=self.padY)

	def buttonRelatedAddSetup(self):
		button = Button(self.frameThought, text=self.addRelatedText[False], command=self.addRelatedButton)
		self.buttonRelatedAdd = button
		button.grid(column=0, row=1, sticky='ew', padx=self.padX, pady=self.padY)

	def buttonRelatedRemoveSetup(self):
		button = Button(self.frameThought, text=self.removeRelatedText[False], command=self.removeRelatedButton)
		self.buttonRelatedRemove = button
		button.grid(column=1, row=1, sticky='ew', padx=self.padX, pady=self.padY)

	def buttonOffspringShowSetup(self):
		button = Button(self.frameThought, text="Show related to this")
		self.buttonRelatedAdd = button
		button.grid(column=0, row=1, sticky='ew', padx=self.padX, pady=self.padY)

	def showRelated(self):
		if self.displayID != self.displayIDNone:
			thought = self.stream.getThought(self.displayID)
			rel = thought.related()
			relIDs = []
			for r in rel:
				relIDs.append(r.id())

			self.updateTable(relIDs)

	def addRelatedButton(self):
		if not self.removingRelated:
			if self.addingRelated:
				self.manipulateRelated()
				self.addingRelated = False
			else:
				self.addingRelated = True
			self.buttonRelatedAdd.config(text=self.addRelatedText[self.addingRelated])

	def removeRelatedButton(self):
		if not self.addingRelated:
			if self.removingRelated:
				self.manipulateRelated()
				self.removingRelated = False
			else:
				self.removingRelated = True
			self.buttonRelatedRemove.config(text=self.removeRelatedText[self.removingRelated])

	def manipulateRelated(self):
		if self.displayID != self.displayIDNone:
			selection : list[int] = self.getSelectedIDs()
			thought : Thought = self.stream.getThought(self.displayID)
			relList : list[Thought] = []
			for ID in selection:
				relList.append(self.stream.getThought(ID))

			if self.addingRelated:
				thought.addRelatedList(relList)

			if self.removingRelated:
				thought.removeRelatedList(relList)

		self.stream.saveToJSON()
		self.updateTable()


	def styleSetup(self):
		s = self.style
		windows = [self, ]
		frames = [
				self.frameTable,
		]
		labelframes = [
				self.frameThought,
				self.frameStream,
		]
		entrys = [
				self.entryThought,
				self.entryStream,
		]
		tables = [
				self.tableStream,
		]
		texts = [
				self.textThought,
		]
		buttons = [
				self.buttonDelete,
				self.buttonStream,
				self.buttonRelatedShow,
				self.buttonRelatedAdd,
				self.buttonRelatedRemove,
		]
		checks = [
				self.checkRelated,
		]
		labels = [
				self.labelStream,
				self.labelThought,
		]
		options = [
				self.optionStream,
		]

		for window in windows:
			window["bg"] = s["cbg1"]

		for frame in frames:
			frame["bg"] = s["cbg1"]

		for labelframe in labelframes:
			labelframe["bg"] = s["cbg1"]
			labelframe["fg"] = s["cText"]
			labelframe["bd"] = 1
			# labelframe["highlightbackground"] = s["cWindow"]

		for entry in entrys:
			entry["bg"] = s["cbg2"]
			entry["fg"] = s["cText"]
			entry["bd"] = 1
			entry["relief"] = SUNKEN

		style = ttk.Style()
		style.theme_use("default")
		style.configure("Treeview",
						background=s["cbg1"],
						foreground=s["cText"],
						fieldbackground=s["cbg1"],
						# font=s["fText"]
						)
		style.configure("Treeview.Heading",
						background=s["cbg1"],
						foreground=s["cText"],
						)
		style.map("Treeview",
				  background=[('selected', s["cbg2"])])

		for text in texts:
			text["bg"] = s["cbg2"]
			text["fg"] = s["cText"]
			text["bd"] = s["borderFlush"]
			text["font"] = s["fTextLarge"]

		for button in buttons:
			button["bg"] = s["cbg2"]
			button["activebackground"] = s["cbg3"]
			button["fg"] = s["cText"]
			button["activeforeground"] = s["cText"]
			button["bd"] = s["borderFlush"]

		for check in checks:
			check["bg"] = s["cbg1"]
			check["fg"] = s["cText"]
			check["activebackground"] = s["cbg1"]
			check["activeforeground"] = s["cText"]
			check["selectcolor"] = s["cbg2"]

		for label in labels:
			label["bg"] = s["cbg1"]
			label["fg"] = s["cText"]

		for option in options:
			option["bg"] = s["cbg2"]
			option["fg"] = s["cText"]
			option["activebackground"] = s["cbg3"]
			option["activeforeground"] = s["cText"]
			option["bd"] = s["borderFlush"]
			option["highlightthickness"] = s["borderFlush"]
			option["menu"]["bg"] = s["cbg3"]
			option["menu"]["fg"] = s["cText"]

	def afterStyleSetup(self):
		self.entryStreamFocusOut(0)



main = MainWindow()
