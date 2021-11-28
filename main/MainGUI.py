from tkinter import *
from tkinter import ttk

from Thought import Thought
from Stream import Stream


class MainWindow(Tk):
	# Default settings
	wWidth = 1024
	wHeight = 600
	wOffsetX = 450
	wOffsetY = 200
	wTitle = "Stream"

	# GUI elements
	lStart = 0
	lEnd = 200
	rStart = 200
	rEnd = 1024
	padX = 5
	padY = 5
	entryStream : Entry
	tableStream : ttk.Treeview
	textThought : Text
	buttonDelete : Button
	checkRelated : Checkbutton
	textRelated : Text

	# TableStream settings
	tableStreamColumns : list[str] = ["date", "time", "thought"]

	# Stream saves
	stream : Stream
	streamDefault : str = "default"

	# CheckRelated vars
	checkRelatedVal : IntVar

	def __init__(self):
		super().__init__()
		self.windowSetup()
		self.environmentSetup()
		self.mainloop()


	def windowSetup(self):
		self.title(self.wTitle)
		self.geometry(str(self.wWidth) + "x" + str(self.wHeight) + "+" + str(self.wOffsetX) + "+" + str(self.wOffsetY))


	def environmentSetup(self):
		self.stream = Stream(self.streamDefault)
		self.stream.loadFromJSON()
		self.tableSetup()
		self.entryStreamSetup()
		self.textThoughSetup()
		self.buttonDeleteSetup()
		self.relatedSetup()


	def tableSetup(self):
		table = ttk.Treeview(self)
		self.tableStream = table

		# Columns
		table["columns"] = self.tableStreamColumns
		table.column("#0", anchor=W, width=50, minwidth=50)
		table.column("date", anchor=CENTER, width=60, minwidth=60)
		table.column("time", anchor=CENTER, width=60, minwidth=60)
		table.column("thought", anchor=W, width=625, minwidth=500)

		# Headings
		table.heading("#0", text="#")
		table.heading("date", text="Date")
		table.heading("time", text="Time")
		table.heading("thought", text="Thought")

		# Data
		self.updateTable()

		# Positioning
		table.pack()
		table.grid(column=1, row=1, padx=self.padX, pady=0, rowspan=2)

		# Binding
		table.bind("<ButtonRelease-1>", self.updateTextThought)

		# Settings
		# table["selectmode"] = "browse"
		table["height"] = 27

		# Scrollbar - Not strictly necessary, as the treeview can scroll on it's own
		# scroll = ttk.Scrollbar(self, orient="vertical", command=table.yview)
		# scroll.grid(column=1, row=1, rowspan=2, sticky='ns')

	def updateTable(self):
		table = self.tableStream
		for item in table.get_children():
			table.delete(item)

		thoughts : dict[int, Thought] = self.stream.getThoughts()
		for tID in thoughts:
			thought = thoughts[tID]
			info = (thought.timeStrDate(), thought.timeStrTime(), thought.text())
			table.insert(parent='', index='end', iid=tID, text=str(tID), values=info)

	def updateTableSingle(self, thoughtID):
		thought = self.stream.getThought(thoughtID)
		info = (thought.timeStrDate(), thought.timeStrTime(), thought.text())
		self.tableStream.insert(parent='', index='end', iid=thought.id(), text=str(thought.id()), values=info)

	def getSelectedIDs(self) -> list[int]:
		# TODO: extend later with child formatting
		s = []
		for ID in self.tableStream.selection():
			s.append(int(ID))
		return s


	def entryStreamSetup(self):
		entry = Entry(self, exportselection=0, width=110)
		entry.grid(column=1, row=3, sticky='w', padx=self.padX, pady=self.padY)
		entry.bind("<Return>", self.entryCreateThought)
		self.entryStream = entry

	def entryCreateThought(self, a):
		# Create the thought
		text = self.entryStream.get()
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
		self.entryStream.delete(0, len(text))


	def textThoughSetup(self):
		text = Text(self, width=25, padx=2, height=1)
		self.textThought = text
		text.grid(column=0, row=2, sticky='ns', padx=self.padX)
		text.insert(END, "uwu")
		text.bind("<Return>", self.textThoughtUpdate)

	def updateTextThought(self, a):
		selection = self.getSelectedIDs()
		if len(selection) == 0:
			self.textThought.delete(1.0, END)

		if len(selection) == 1:
			self.textThought.delete(1.0, END)
			ID = int(selection[0])
			thought : Thought = self.stream.getThought(ID)
			self.textThought.insert(1.0, thought.text())

	def textThoughtUpdate(self, a):
		selection = self.getSelectedIDs()
		if len(selection) == 1:
			ID = int(selection[0])
			thought : Thought = self.stream.getThought(ID)
			thought.setText(self.textThought.get(1.0, 'end-1c'))		# Edit the thought (have to keep the trailing \n in mind)
			self.stream.saveToJSON()									# Save the stream
			self.updateTable()											# Update the entire table
			self.textThought.delete(1.0, END)							# Re-update the text with the updated text
			self.textThought.insert(1.0, thought.text())


	def buttonDeleteSetup(self):
		button = Button(self, text="Delete Thought", command=self.deleteThought)
		self.buttonDelete = button
		button.grid(column=0, row=3, sticky='ew', padx=2*self.padX, pady=self.padY)

	def deleteThought(self):
		selection = self.getSelectedIDs()
		if len(selection) == 0:
			return

		for sID in selection:
			self.stream.removeThought(sID)

		self.stream.saveToJSON()
		self.updateTable()


	def relatedSetup(self):
		self.checkRelatedVal = IntVar()
		check = Checkbutton(self, text="Related to selection", variable=self.checkRelatedVal)
		self.checkRelated = check
		check.grid(column=1, row=3, sticky='e')

		# text = Text(self, width=62, padx=2, height=1)
		# self.textRelated = text
		# text.grid(column=1, row=4, sticky='e')



main = MainWindow()
