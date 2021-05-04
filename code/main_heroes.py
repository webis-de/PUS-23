import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, colors
from os.path import basename, exists, sep
from os import makedirs

#######################################################################
# This file serves as an entry point to plot Wikipedia article heroes.#
#######################################################################

rc('xtick', labelsize=15)
rc('ytick', labelsize=15)

PATH = "../data/"
df1 = pd.read_pickle(PATH + 'heroes_CRISPR_en.pickle')
df2 = pd.read_pickle(PATH + 'heroes_CRISPR_gene_editing_en.pickle')
hero_frames = [df1, df2]
fig = plt.figure(figsize=(20,9), dpi=400)
axs = [plt.subplot2grid((10, 20), (0, 0), colspan=15, rowspan=10),
       plt.subplot2grid((10, 20), (0, 15), colspan=5, rowspan=10)]
first_subplot = True

names1 = df1[(df1['controversiality']==1) & (df1['prominence']<.5) & (df1['prominence']>=.1)]['name'].to_list()
names2 = df1[(df1['controversiality']==1) & (df1['prominence']<.1) & (df1['prominence']>=.01)]['name'].to_list()
names3 = df1[(df1['controversiality']==1) & (df1['prominence']<.01)]['name'].to_list()

for i, df in enumerate(hero_frames):
    xytextdict = {}
    
    ax = axs[i]
    x = df['controversiality']
    xlabel = 'Controversiality'
    y = df['prominence']
    ylabel = 'Prominence'
    hue = df['age']
    hue_label = '      older ⟷ younger\nAge' # '      older ⟵ Age ⟶ younger'
    size = df['endurance']    
    size_label = 'Endurance99'
    labels = df['name']
    ax.scatter(
        x=x, y=y, 
        c=hue, 
        s=size * 500,
        cmap='gist_yarg',
        edgecolors='black',
    )
    labels = []

    for index, (xi,yi) in enumerate(zip(x,y)): # https://queirozf.com/entries/add-labels-and-text-to-matplotlib-plots-annotation-examples
        label = df['name'].iloc[index]
        if label in names1 or label in names2 or label in names2:
            addx = -0.5
            addy = -0.2
        elif label == "Šikšnys" and df['controversiality'][index] == 0 and df['prominence'][index] == 2:
            addx = 0.5
            addy = 0.2
        elif label == "Haft":
            addx = 0.5
            addy = 0.2
        elif label == "Sinclair":
            addx = -0.5
            addy = 0.2
        elif label == "Jinek":
            addx = 0.5
            addy = -0.2
        else:
            if xi not in xytextdict:
                xytextdict[xi] = {}
            if yi not in xytextdict[xi]:
                xytextdict[xi][yi] = [0, 0.125]
            addx = xytextdict[xi][yi][0]
            addy = xytextdict[xi][yi][1]
            xytextdict[xi][yi][0] += 0
            xytextdict[xi][yi][1] += 0.1

        endurance_shift = 0 #0.04 if df['endurance'].iloc[index] < 0.5 else 0
        xytext = (xi + addx, yi + addy - endurance_shift) # position of text (x,y)
        
        if label in names1:
            xytext = (xytext[0], xytext[1]+xytext[1]*0.5)
            if label not in ["Vergnaud", "Bolotin"]:
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='right', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=2,angleB=50",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Vergnaud":
                ax.annotate(
                    "Vergnaud, Bolotin", # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='right', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=-5,angleB=50",facecolor='black'),
                    fontsize=11,
                )
        elif label == names2[-1]:
            xytext = (xi + 0.5,
                      yi - 0.1)
            ax.annotate(
                ", ".join(names2), # this is the text
                (xi,yi), # this is the point to label
                textcoords="data", # how to position the text
                xytext=xytext, # position of text (x,y)
                ha='left', # position of the text to points
                arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=2,angleB=-30",facecolor='black'),
                fontsize=11,
            )
        elif label == names3[-1]:
            xytext = (xi + 0.5,
                      yi - 0.2)
            ax.annotate(
                ", ".join(names3), # this is the text
                (xi,yi), # this is the point to label
                textcoords="data", # how to position the text
                xytext=xytext, # position of text (x,y)
                ha='left', # position of the text to points
                arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=3,angleB=-60",facecolor='black'),
                fontsize=11,
            )
        if not any([label in names for names in [names1, names2, names3]]):
            if label == "Šikšnys" and df['controversiality'][index] == 0 and df['prominence'][index] == 2:
                xytext = (xi + 0.5,
                      yi - 0.2)
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='center', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=0,angleB=-60",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Haft":
                xytext = (xi + 0.5, yi + 0.2)
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='left', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=0,angleB=-120",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Sinclair":
                xytext = (xi - 0.5, yi + 0.2)
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='center', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=15,angleB=120",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Jinek":
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='left', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=0,angleB=120",facecolor='black'),
                    fontsize=11,
                )
            else:
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # position of text (x,y)
                    ha='center', # position of the text to points
                    arrowprops=None,
                    fontsize=11,
                )

    ax.set_title(("\"CRISPR\"" if i == 0 else "\"CRISPR gene editing\"") + " (C" + str(i+1) + ")", fontsize="xx-large")
    ax.set_xlabel(xlabel, fontsize="xx-large")
    ax.set_xlim(-0.5, xmax=8.5 if first_subplot else 1.5)
    if first_subplot:
        ax.set_ylabel(ylabel, fontsize="xx-large")
        first_subplot = False
    else:
        ax.set_xticks([0,1])
        ax.set_yticks([])
    ax.set_ylim(ymin=-0.25, ymax=4.25)

for i in [0.1, 0.5, 1.0]:
    plt.scatter([], [], c='w', s=i * 500, label=str(i), edgecolor='k')
plt.legend(scatterpoints=1, frameon=True, edgecolor="k", fancybox=True, labelspacing=2, title=size_label, borderpad=1.2, title_fontsize="x-large")
plt.subplots_adjust(bottom=0.075, top=0.96, left=0.04, right=0.965)

cmap_gradient = 2000
cmap_ticks = 11
cmap_start = 0
cmap_stop = 1
cmap = plt.get_cmap('gist_gray', cmap_gradient)
norm = colors.Normalize(vmin=cmap_start, vmax=cmap_stop)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ticks=[]) #ticks=[i for i in np.linspace(cmap_start,cmap_stop,11)]

cbar.ax.set_ylabel(hue_label, fontsize="xx-large")
if not exists('../analysis/heroes'):
    makedirs('../analysis/heroes')
plt.savefig('../analysis/heroes/heroes_plot_combined.png')
plt.savefig('../analysis/heroes/heroes_plot_combined.pdf')
