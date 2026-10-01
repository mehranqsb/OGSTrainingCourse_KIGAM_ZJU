// Structured quad mesh with ONE fracture group
// ------------------------------------------------
// Visualization
Geometry.PointNumbers = 1;
Geometry.LineNumbers = 1;
Geometry.SurfaceNumbers = 1;
Geometry.VolumeNumbers = 1;

Geometry.Color.Points = Red;
Geometry.Color.Lines = Blue;
Geometry.Color.Surfaces = Green;
Geometry.Color.Volumes = Gold;

General.Color.Text = Black;

// ----------------------------
// Parameters
cube_width  = 12.6;
cube_height = 1.;
frac =  0.5;
lc = 1;

// ----------------------------
// Corner and split points
Point(1) = {0.1,          0.,           0., lc};
Point(2) = {cube_width,   0.,           0., lc};
Point(3) = {cube_width,   cube_height,  0., lc};
Point(4) = {cube_width,   frac,         0., lc};
Point(5) = {0.1,          cube_height,  0., lc};
Point(6) = {0.1,          frac,         0., lc};
//+
Line(1) = {1, 2};
Line(2) = {2, 4};
Line(3) = {4, 3};
Line(4) = {6, 4};
Line(5) = {1, 6};
Line(6) = {6, 5};
Line(7) = {5, 3};
//+
Curve Loop(1) = {-5, -4, 2, 1};
Plane Surface(1) = {1};
//+
Curve Loop(2) = {-6, -7, 3, 4};
Plane Surface(2) = {2};
//+
nx = 35;
ny = 20;
pfac_b = 0.9;
pfac_t = 1.1;
bfac = 4.2;
Transfinite Curve {1, 4} = nx Using Progression 1;
Transfinite Curve {2, 5} = ny Using Progression pfac_b;
Transfinite Surface {1} = {1, 2, 4, 6};
//+
Transfinite Curve {4, 7} = nx Using Progression 1;
Transfinite Curve {3, 6} = ny Using Progression pfac_t;
Transfinite Surface {2} = {6, 4, 3, 5};
//+
Recombine Surface{1, 2};
Mesh.RecombineAll = 1;
Physical Surface("ROCK", 201) = {1, 2};
Physical Curve("FRACTURE", 101) = {4};

Mesh 2;
Coherence Mesh;
