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
	4. Double-click on this file (calc_stats.py)
	
	The results will be written to several files with a ".tab" ending. These are tab-delimited files that can
	be read into Excel. They include "mean.tab", "min.tab", "max.tab", "q25.tab", "q50.tab" and "q75.tab"

"""
def sign(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    elif x == 0:
        return 0.
    else:
        return x

import re
scenvar_patt = re.compile("^S([0-9]+)\ (.+)")
avg_mean=dict()
q25=dict() # Example: 2nd quartile
s25=dict()
q50=dict() # Example: median
s50=dict()
q75=dict() # Example: 3rd quartile
s75=dict()
xmin=dict()
xmax=dict()
print("Calculating...")
with open('results.tab', 'r') as fin:
	for currline in fin:
		linelist = currline.rstrip().split("\t")
		scenvar = linelist[0]
		vals = linelist[1:]
		if scenvar == "Time":
			years = linelist
		else:
			m = scenvar_patt.match(scenvar)
			scennum = int(m.group(1))
			var = m.group(2)
			if var == "NOISE SEED":
				if scennum % 1000 == 0:
					print(str(scennum) + " scenarios averaged...")
				continue
			if int(scennum) == 1:
				# This sets the dimension
				avg_mean[var] = [0.0] * len(vals)
				xmax[var] = [0.0] * len(vals)
				xmin[var] = [0.0] * len(vals)
				q25[var] = [0.0] * len(vals)
				q50[var] = [0.0] * len(vals)
				q75[var] = [0.0] * len(vals)
				s25[var] = [0.0] * len(vals)
				s50[var] = [0.0] * len(vals)
				s75[var] = [0.0] * len(vals)
				# Initialize to first scenario value for all years (j indexes over years, here)
				for j in range(0,len(vals)):
					curr_val = float(vals[j])
					avg_mean[var][j] = curr_val
					xmax[var][j] = curr_val
					xmin[var][j] = curr_val
					q25[var][j] = curr_val
					q50[var][j] = curr_val
					q75[var][j] = curr_val
			else:
				for j in range(0,len(vals)):
					curr_val = float(vals[j])
					avg_mean[var][j] = avg_mean[var][j] + (curr_val - avg_mean[var][j])/scennum
					xmax[var][j] = max(xmax[var][j],curr_val)
					xmin[var][j] = min(xmin[var][j],curr_val)
					s25[var][j] = s25[var][j] + ((abs(q25[var][j] - curr_val) + s25[var][j])/scennum - 2.0*s25[var][j])/scennum
					s50[var][j] = s50[var][j] + ((abs(q50[var][j] - curr_val) + s50[var][j])/scennum - 2.0*s50[var][j])/scennum
					s75[var][j] = s75[var][j] + ((abs(q75[var][j] - curr_val) + s75[var][j])/scennum - 2.0*s75[var][j])/scennum
					q25[var][j] = q25[var][j] + 1.5 * s25[var][j] * (sign(curr_val - q25[var][j]) + 2.0 * 0.25 - 1.0)
					q50[var][j] = q50[var][j] + 1.5 * s50[var][j] * (sign(curr_val - q50[var][j]) + 2.0 * 0.50 - 1.0)
					q75[var][j] = q75[var][j] + 1.5 * s75[var][j] * (sign(curr_val - q75[var][j]) + 2.0 * 0.75 - 1.0)
fin.close()

penalty = pow(scennum,0.66) # This was found by trial and error, used below

print("Done")
# Write out means
fout = open('mean.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(avg_mean.keys()):
	fout.write(k + "\t" + "\t".join(map(str,avg_mean[k])) + "\n")
fout.close()
# Write out mins
fout = open('min.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(xmin.keys()):
	fout.write(k + "\t" + "\t".join(map(str,xmin[k])) + "\n")
fout.close()
# Write out maxes
fout = open('max.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(xmax.keys()):
	fout.write(k + "\t" + "\t".join(map(str,xmax[k])) + "\n")
fout.close()
# Write out q25
fout = open('q25.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(q25.keys()):
	pmin = (1 - 0.25)**penalty
	pmax = 0.25**penalty
	for i in range(0,len(q25[k])-1):
		q25[k][i] = pmin * xmin[k][i] + pmax * xmax[k][i] + (1 - pmin - pmax) * q25[k][i]
	fout.write(k + "\t" + "\t".join(map(str,q25[k])) + "\n")
fout.close()
# Write out q50
fout = open('q50.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(q50.keys()):
	pmin = (1 - 0.50)**penalty
	pmax = 0.50**penalty
	for i in range(0,len(q50[k])-1):
		q50[k][i] = pmin * xmin[k][i] + pmax * xmax[k][i] + (1 - pmin - pmax) * q50[k][i]
	fout.write(k + "\t" + "\t".join(map(str,q50[k])) + "\n")
fout.close()
# Write out q75
fout = open('q75.tab','w')
fout.write("\t".join(years) + "\n")
for k in sorted(q75.keys()):
	pmin = (1 - 0.75)**penalty
	pmax = 0.75**penalty
	for i in range(0,len(q75[k])-1):
		q75[k][i] = pmin * xmin[k][i] + pmax * xmax[k][i] + (1 - pmin - pmax) * q75[k][i]
	fout.write(k + "\t" + "\t".join(map(str,q75[k])) + "\n")
fout.close()
