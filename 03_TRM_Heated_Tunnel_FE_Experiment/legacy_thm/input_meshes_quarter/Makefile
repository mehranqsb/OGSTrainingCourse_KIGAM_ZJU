# source ~/.venv/bin/activate

msh:
	gmsh Tunnel_Q4.geo -2 -format msh2 -o tunnel.msh

vtu:
	msh2vtu -r tunnel.msh -d 2 -o .

identify:
	identifySubdomains -m tunnel_domain.vtu tunnel_bottom.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_right.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_top.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_left.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_arc_inner.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_arc_outer.vtu -f
	identifySubdomains -m tunnel_domain.vtu tunnel_pt0.vtu -f

all:
	make msh && make vtu && make identify

clean:
	rm -rf *.vtu  \#* input_meshes *~ *.msh *.yaml

