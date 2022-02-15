from farm import *


x = load_all_farms()

locs = {
    "production": [
        "field",
        "garden",
        "barn",
        "greenhouse",
        "residence",
    ],
    "natural": [
        "farm_site_boundary",
        "natural_area",
        "surface_water",

    ]

}


data = []
for f in x:
    if f.total_area < 1:
        continue
    else:

        nat  = []
        prod = []
        for loc in f.locations:
            if loc in  locs['natural']:
                nat.extend(f.locations[loc])
            if loc in  locs['production']:
                prod.extend(f.locations[loc])

        data.append({
            "farmid"   : f.farm_id,
            "totalarea": f.total_area,
            "nat"      : unary_union(nat).area,
            "prod"     : unary_union(prod).area
        })
            



w      = 0.6
totals = list(map(lambda x: x['totalarea'], data))
prods  = list(map(lambda x: x['prod'], data))
nats   = list(map(lambda x: x['nat'], data))

data.sort(key=lambda x: x['totalarea'])

x= np.array_split(np.array(data),10)
subarrs =[]
for i in x:
    total = 0
    nat   = 0
    prod  = 0
    for sub in i:
        total += sub['totalarea']
        prod  += sub['prod']
        nat   += sub['nat']
    subarrs.append({
        "total": total,
        "prod" : prod,
        "nat"  : nat
    })
        
fig,ax =plt.subplots()
ax.bar(np.arange(10),list(map(lambda x: x['prod'],subarrs)), width=0.2, color="None",edgecolor="black")
ax.bar(np.arange(10),list(map(lambda x: x['nat'],subarrs)), width=0.2,bottom=list(map(lambda x: x['prod'],subarrs)), color="green", edgecolor='black')

# Add labels
ax.set_xlabel("(Size by Area) Percentile")
ax.set_ylabel("Total Area")

for i, v in enumerate(subarrs):
    ax.text(i, i + .25, str(v['total']), color='blue', fontweight='bold')

patches = [
Patch(facecolor="green", label= "Natural Areas"   .format(         )),
Patch(facecolor="black", label= "Industrial Areas".format(         )),
Patch(facecolor=None,fill=None, label= "Total farms: {}" .format(len(data)))
           ]

plt.title("Distribution of Natural vs Industrial Areas")
handles, _ = ax.get_legend_handles_labels()
plt.legend(handles=[*patches], loc='best')
# Display

plt.show()