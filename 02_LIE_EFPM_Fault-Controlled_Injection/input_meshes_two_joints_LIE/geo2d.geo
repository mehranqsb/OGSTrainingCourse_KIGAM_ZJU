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
frac0 =  0.3;
frac1 =  0.7;
lc = 1;

// ----------------------------
// Corner and split points
Point(1) = {0.1,         0.,           0, lc};
Point(2) = {cube_width,  0.,           0, lc};
Point(3) = {cube_width,  frac0,        0, lc};
Point(4) = {cube_width,  frac1,        0, lc};
Point(5) = {cube_width,  cube_height,  0, lc};
Point(6) = {0.1,         cube_height,  0, lc};
Point(7) = {0.1,         frac1,        0, lc};
Point(8) = {0.1,         frac0,        0, lc};
//+
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {1, 8};
Line(4) = {8, 3};
Line(5) = {3, 4};
Line(6) = {8, 7};
Line(7) = {7, 4};
Line(8) = {4, 5};
Line(9) = {7, 6};
Line(10) = {6, 5};
//+
Curve Loop(1) = {-3, -4, 2, 1};
Plane Surface(1) = {1};
//+
Curve Loop(2) = {-6, -7, 5, 4};
Plane Surface(2) = {2};
//+
Curve Loop(3) = {-9, -10, 8, 7};
Plane Surface(3) = {3};
//+
Transfinite Surface {1, 2, 3};
Transfinite Curve {1, 4, 7, 10} = 35 Using Bump 1;
Transfinite Curve {2, 3} = 15 Using Progression 0.8;
Transfinite Curve {5, 6} = 25 Using Bump 0.1;
Transfinite Curve {9, 8} = 15 Using Progression 1/0.8;
//+
Recombine Surface {1, 2, 3};
Mesh.RecombineAll = 1;

Physical Surface("ROCK", 201) = {1, 2, 3};
Physical Curve("FRACTURE0", 101) = {4};
Physical Curve("FRACTURE1", 102) = {7};
Mesh 2;
Coherence Mesh;
