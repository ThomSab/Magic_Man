import os

base_path = r'C:\Users\X250\Magic_Man'
dirlist = [_ if "Bots_" in _ else None for _ in os.listdir(base_path)]
while None in dirlist:
	for _ in dirlist:
		if _ == None:
			dirlist.remove(_)


lr_given = False
while not lr_given:
	print("Which Pool do you want to access?")
	for pool in dirlist:
		print("[",dirlist.index(pool),"]", pool)

	lr_answer  = input("\n")
	try:
		lr_idx = int(lr_answer)
		if lr_idx > len(dirlist) or lr_idx < 0:
			print("DIR DOES NOT EXIST")
		else:
			lr = dirlist[lr_idx].split('_')[-1]
			lr_given = True
	except ValueError:
		print("Answer must be one of the indexes")


bot_dir   = '\\' + dirlist[lr_idx]
