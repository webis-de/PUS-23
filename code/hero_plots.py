import pandas as pd
import matplotlib.pyplot as plt

PATH = ""
df1 = pd.read_pickle(PATH + 'heroes_CRISPR_en.pickle')
df2 = pd.read_pickle(PATH + 'heroes_CRISPR_gene_editing_en.pickle')
hero_frames = [df1, df2]
##f, axs = plt.subplots(1, 2, sharey=True, sharex=True, figsize=(6, 3), dpi=200, facecolor='white')
fig = plt.figure(figsize=(20,10))
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

        if label in names1 or label in names2 or label in names2:
            addx = -1
            addy = -0.2
        else:
            if xi not in xytextdict:
                xytextdict[xi] = {}
            if yi not in xytextdict[xi]:
                xytextdict[xi][yi] = [0, 0.1]
            addx = xytextdict[xi][yi][0]
            addy = xytextdict[xi][yi][1]
            xytextdict[xi][yi][0] += 0
            xytextdict[xi][yi][1] += 0.1
        
        xytext = (xi + addx, yi + addy) # distance from text to points (x,y)
        
        if label in names1:
            xytext = (xytext[0], xytext[1]+xytext[1]*0.5)
            if label not in ["Vergnaud", "Bolotin"]:
                ax.annotate(
                    label, # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='left', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=2,angleB=30",facecolor='black'),
                    fontsize=11,
                )
            elif label == "Vergnaud":
                ax.annotate(
                    "Vergnaud, Bolotin", # this is the text
                    (xi,yi), # this is the point to label
                    textcoords="data", # how to position the text
                    xytext=xytext, # distance from text to points (x,y)
                    ha='left', # position of the text to points
                    arrowprops=dict(arrowstyle="->",connectionstyle="angle3,angleA=2,angleB=30",facecolor='black'),
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
            ax.annotate(
                label, # this is the text
                (xi,yi), # this is the point to label
                textcoords="data", # how to position the text
                xytext=xytext, # distance from text to points (x,y)
                ha='center', # position of the text to points
                arrowprops=None,#dict(arrowstyle="->",connectionstyle="angle3,angleA=0,angleB=-90",facecolor='black'),
                fontsize=11,
            )

    ax.set_title('C' + str(i+1))
    ax.set_xlabel(xlabel)
    ax.set_xlim(-0.5, xmax=8.5 if handle_yaxis else 1.5)
    if handle_yaxis:
        ax.set_ylabel(ylabel)
        handle_yaxis = False
    else:
        ax.set_xticks([0,1])
        ax.set_yticks([])
    ax.set_ylim(ymin=-0.25, ymax=4.25)

    # # add color scale for hue
#cbar = plt.colorbar()  # show color scale
    #cbar.ax.set_ylabel(hue_label)
    
for i in [.1, .5, 1., ]:
    plt.scatter([], [], c='k', alpha=0.2, s=i * 500, label=str(i) )
plt.legend(scatterpoints=1, frameon=False, fancybox=True, labelspacing=2, title=size_label,)
plt.subplots_adjust(bottom=0.06, top=0.97, left=0.03, right=0.98)
cbar = plt.colorbar()
cbar.ax.set_ylabel(hue_label)
plt.savefig(PATH + 'heroes_plot_combined.png')
