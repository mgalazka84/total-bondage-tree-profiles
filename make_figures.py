"""Create the three paper figures using exact graph data (no generated imagery)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import networkx as nx
from bondage import bondage_profile
from bruteforce import total_domination
from families import spider, formula

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'pdf.fonttype': 42, 'axes.spines.top': False,
                     'axes.spines.right': False})
out = Path('figures')
out.mkdir(exist_ok=True)

# Figure 1: a rigorously verifiable network example.
n, edges = spider(1)
pos = {i: (i*.85, 0) for i in range(8)}
pos.update({8: (-.65, .55), 9: (-1.3, 1.0),
            10: (-.65, -.55), 11: (-1.3, -1.0)})
labels = {0: 'c', **{i: f'$v_{i}$' for i in range(1,8)},
          8: '$a_1$', 9: '$a_2$', 10: '$b_1$', 11: '$b_2$'}
fig, axes = plt.subplots(3, 1, figsize=(7.1, 6.4))
cases = [((), '(a) Original tree: 7 stations'),
         ((7,), '(b) One optimal deletion: 8 stations'),
         ((3,5), '(c) Two optimal deletions: 9 stations')]
for ax, (removed, title) in zip(axes, cases):
    graph = nx.Graph(); graph.add_nodes_from(range(n)); graph.add_edges_from(edges)
    remaining = [e for i,e in enumerate(edges) if i not in removed]
    value, chosen = total_domination(n, remaining, return_set=True)
    nx.draw_networkx_edges(graph, pos, edgelist=remaining, ax=ax, width=1.3, edge_color='#4b5563')
    nx.draw_networkx_edges(graph, pos, edgelist=[edges[i] for i in removed], ax=ax,
                           width=1.7, style='dashed', edge_color='#b52e31')
    for selected in (False, True):
        nodes = [v for v in range(n) if (v in chosen) == selected]
        nx.draw_networkx_nodes(graph, pos, nodelist=nodes, ax=ax, node_size=350,
                               node_color='#233650' if selected else 'white',
                               edgecolors='#233650', linewidths=1.1)
        nx.draw_networkx_labels(graph, pos, labels={v:labels[v] for v in nodes},
                                ax=ax, font_size=9,
                                font_color='white' if selected else '#233650')
    ax.text(-1.7, 1.4, title, fontsize=10.5, weight='bold')
    ax.set_xlim(-1.8, 6.4); ax.set_ylim(-1.35,1.65); ax.axis('off')
fig.legend(handles=[Line2D([],[],marker='o',color='none',markerfacecolor='#233650',
                           markeredgecolor='#233650',label='station'),
                    Line2D([],[],color='#b52e31',linestyle='--',label='deleted edge')],
           loc='lower center', ncol=2, frameon=False, bbox_to_anchor=(.5,.005))
fig.tight_layout(rect=[0,.045,1,1]);fig.savefig(out/'network_example.pdf',bbox_inches='tight')
fig.savefig(out/'network_example.png',dpi=170,bbox_inches='tight');plt.close(fig)

# Figure 2: the two compositions at an edge.
fig, axes=plt.subplots(1,2,figsize=(7.1,2.75))
for ax, removed in zip(axes,(False,True)):
    for x,label,root in [(0,'A','u'),(2.2,'B','v')]:
        ax.add_patch(Polygon([[x,-.12],[x-.65,-1.1],[x+.65,-1.1]],
                              fc='#eef2f7',ec='#8894a3',lw=1.1))
        ax.text(x,-.78,label,ha='center',fontsize=14)
        ax.plot(x,0,'o',color='white',markeredgecolor='#233650',markersize=13,zorder=3)
        ax.text(x,.25,root,ha='center',fontsize=12)
    ax.plot([0,2.2],[0,0],color='#b52e31' if removed else '#233650',
            ls='--' if removed else '-',lw=2,zorder=2)
    ax.text(1.1,.65,'Cut the edge' if removed else 'Keep the edge',
            ha='center',fontsize=11,weight='bold')
    ax.text(1.1,-1.45,'Root v must be dominated\ninside B.' if removed else
            'Selected endpoints can\ndominate across the edge.',
            ha='center',va='top',fontsize=10)
    ax.set_xlim(-.9,3.1);ax.set_ylim(-2.1,1.0);ax.axis('off')
fig.tight_layout();fig.savefig(out/'root_composition.pdf',bbox_inches='tight')
fig.savefig(out/'root_composition.png',dpi=170,bbox_inches='tight');plt.close(fig)

# Figure 3: exact profiles, not fitted curves.
fig, ax=plt.subplots(figsize=(6.8,3.6))
for r,color,mark in [(1,'#233650','o'),(2,'#b16b13','s'),(3,'#43775b','^')]:
    p=formula(r)
    ax.plot(range(len(p)),p,marker=mark,color=color,label=f'$r={r}$, $n={4*r+8}$',lw=1.5)
ax.set_xlabel('Required increase $k$ in total domination number')
ax.set_ylabel('Minimum edge deletions $b_t^k$')
ax.set_xticks(range(10));ax.set_yticks(range(10));ax.grid(alpha=.18)
ax.legend(frameon=False,loc='upper left')
fig.tight_layout();fig.savefig(out/'spider_profiles.pdf',bbox_inches='tight')
fig.savefig(out/'spider_profiles.png',dpi=170,bbox_inches='tight');plt.close(fig)
print('Created three exact figures in figures/.')
