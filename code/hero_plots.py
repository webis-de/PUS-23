import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, colors
from math import log

rc('xtick', labelsize=15)
rc('ytick', labelsize=15)

PATH = ""
df1 = pd.read_pickle(PATH + 'heroes_CRISPR_en.pickle')
df2 = pd.read_pickle(PATH + 'heroes_CRISPR_gene_editing_en.pickle')
hero_frames = [df1, df2]
##f, axs = plt.subplots(1, 2, sharey=True, sharex=True, figsize=(6, 3), dpi=200, facecolor='white')
fig = plt.figure(figsize=(20,9), dpi=400)
axs = [plt.subplot2grid((10, 20), (0, 0), colspan=15, rowspan=10),
       plt.subplot2grid((10, 20), (0, 15), colspan=5, rowspan=10)]
handle_yaxis = True

names1 = df1[(df1['controversiality']==1) & (df1['prominence']<.5) & (df1['prominence']>=.1)]['name'].to_list()
names2 = df1[(df1['controversiality']==1) & (df1['prominence']<.1) & (df1['prominence']>=.01)]['name'].to_list()
names3 = df1[(df1['controversiality']==1) & (df1['prominence']<.01)]['name'].to_list()
print(names1)
print(names2)
print(names3)
for i, df in enumerate(hero_frames):
    xytextdict = {}
    
    ax = axs[i]
    x = df['controversiality']
    xlabel = 'Controversiality'
    y = df['prominence']
    ylabel = 'Prominence'
    hue = df['age']
    hue_label = 'First Appearance'
    size = df['endurance']    
    size_label = 'Endurance'
    labels = df['name']
    ax.scatter(
        x=x, y=y, 
        c=hue, 
        s=size * 500,
        alpha=0.3,
        cmap='gist_yarg',
        edgecolors='black',
    )
    labels = []

    for index, (xi,yi) in enumerate(zip(x,y)): # https://queirozf.com/entries/add-labels-and-text-to-matplotlib-plots-annotation-examples
        label = df['name'].iloc[index]
        print(df['endurance'].iloc[index])
        if label in names1 or label in names2 or label in names2:
            addx = -0.5
            addy = -0.2
        elif label == "Yang" and df['controversiality'][index] == 0 and df['prominence'][index] == 2:
            addx = 0.5
            addy = 0.2
        elif label == "Šikšnys" and df['controversiality'][index] == 0 and df['prominence'][index] == 2:
            addx = 0
            addy = 0.225
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
        xytext = (xi + addx, yi + addy - endurance_shift) # distance from text to points (x,y)
        
        if label in names1:
            xytext = (xytext[0], xytext[1]+xytext[1]*0.5)
            if label not in ["Vergnaud", "Bolotin"]:
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='right', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=2,angleB=50",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Vergnaud":
                ax.annotate(
                    "Vergnaud, Bolotin", # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='right', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=-10,angleB=50",facecolor='black'),
                    fontsize=11,
                )
        elif label == names2[-1]:
            xytext = (xi + 0.5,
                      yi - 0.1)
            ax.annotate(
                ", ".join(names2), # this is the text
                (xi,yi), # this is the point to label
                textcoords="data", # how to position the text
                xytext=xytext, # distance from text to points (x,y)
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
                xytext=xytext, # distance from text to points (x,y)
                ha='left', # position of the text to points
                arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=3,angleB=-60",facecolor='black'),
                fontsize=11,
            )
        if not any([label in names for names in [names1, names2, names3]]):
            if label == "Yang" and df['controversiality'][index] == 0 and df['prominence'][index] == 2:
                xytext = (xi + 0.5,
                      yi - 0.2)
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
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
                    xytext=xytext, # distance from text to points (x,y)
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
                    xytext=xytext, # distance from text to points (x,y)
                    ha='center', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=15,angleB=120",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Jinek":
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='left', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=0,angleB=120",facecolor='black'),
                    fontsize=11,
                )
            else:
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='center', # position of the text to points
                    arrowprops=None,
                    fontsize=11,
                )

    ax.set_title(("\"CRISPR\"" if i == 0 else "\"CRISPR gene editing\"") + " (C" + str(i+1) + ")", fontsize="xx-large")
    ax.set_xlabel(xlabel, fontsize="xx-large")
    ax.set_xlim(-0.5, xmax=8.5 if handle_yaxis else 1.5)
    if handle_yaxis:
        ax.set_ylabel(ylabel, fontsize="xx-large")
        handle_yaxis = False
    else:
        ax.set_xticks([0,1])
        ax.set_yticks([])
    ax.set_ylim(ymin=-0.25, ymax=4.25)

    # # add color scale for hue
#cbar = plt.colorbar()  # show color scale
    #cbar.ax.set_ylabel(hue_label)

for i in [.1, .5, 1., ]:
    plt.scatter([], [], c='k', alpha=0.2, s=i * 500, label=str(int(i*2000)) )
plt.legend(scatterpoints=1, frameon=True, fancybox=True, labelspacing=2, title=size_label, borderpad=2, title_fontsize="x-large")
plt.subplots_adjust(bottom=0.075, top=0.96, left=0.04, right=0.965)
cmap = plt.get_cmap('Greys', 2000)
norm = colors.Normalize(vmin=0, vmax=2000)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ticks=[i for i in range(200,2000,200)])
cbar.ax.set_ylabel(hue_label, fontsize="xx-large")
plt.savefig(PATH + 'heroes_plot_combined.png')
