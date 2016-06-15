# File calc_means.py Calculate averages (simple means) of results from a Vensim Monte Carlo run

""" Instructions
	
	1. Within Vensim, do a Monte Carlo run
		a) Click "Monte Carlo" on the toolbar
		b) Check to make sure that all variables you are interested in are in the export list
	2. Export the data set using "Model > Export Dataset..." from the menu and do the following (all are required):
		a) Choose the vdf file corresponding to the run (e.g., "Scenario stochastic.vdf")
		b) Click "Yes" when asked if you want to export the sensitivity results
		c) Select "Across" for "Simulation index/time running"
		d) Select "Simulation Number" for "Modify variable names by"
		e) Select "Prefix" for "Modify names using" (this is the default)
		f) Save to a file called "results.tab"
	3. Wait for results
		a) Open Windows explorer
		b) Keep right-clicking and choosing "Refresh" from the context menu
		c) When the file size of results.tab stops changing, you're done
	4. Double-click on this file (calc_means.py)
	
	The results will be written to a file titled "average.tab". This is a tab-delimited file that can
	be read into Excel.

"""

import re
scenvar_patt = re.compile("^S([0-9]+)\ (.+)")
vars=dict()
print("Calculating...")
curr_scennum = 0
with open('results.tab', 'r') as fin:
	for currline in fin:
		linelist = currline.split("\t")
		scenvar = linelist[0]
		if scenvar == "Time":
			years = linelist
		else:
			m = scenvar_patt.match(scenvar)
			scennum = int(m.group(1))
			var = m.group(2)
			if scennum % 1000 == 0 and scennum != curr_scennum:
				print(str(scennum) + " scenarios averaged...")
				curr_scennum = scennum
			vals = linelist[1:]
			if int(scennum) == 1:
				vars[var] = vals
				for j in range(0,len(vals)-1):
					vars[var][j] = float(vals[j])
			else:
				for j in range(0,len(vals)-1):
					vars[var][j] = vars[var][j] + (float(vals[j]) - vars[var][j])/scennum
fin.close()

print("Done")
fout = open('average.tab','w')
fout.write("\t".join(years))
for k in sorted(vars.keys()):
	fout.write(k + "\t" + "\t".join(map(str,vars[k])))
fout.close()
