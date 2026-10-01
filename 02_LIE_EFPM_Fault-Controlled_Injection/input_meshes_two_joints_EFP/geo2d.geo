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
frac0T =  0.301;
frac0B =  0.3;
frac1T =  0.701;
frac1B =  0.7;
lc = 1;
nx = 35;
// ----------------------------
// Corner and split points
Point(1) = {0.1,         0.,          0., lc};
Point(2) = {cube_width,  0.,          0., lc};
Point(3) = {cube_width,  cube_height, 0., lc};
Point(4) = {0.1,         cube_height, 0., lc};
//+
Point(5) = {cube_width,  frac0B,       0., lc};
Point(6) = {cube_width,  frac0T,       0., lc};
Point(7) = {0.1,         frac0B,       0., lc};
Point(8) = {0.1,         frac0T,       0., lc};
//+
Point(9) = {cube_width,  frac1B,       0., lc};
Point(10)= {cube_width,  frac1T,       0., lc};
Point(11)= {0.1,         frac1B,       0., lc};
Point(12)= {0.1,         frac1T,       0., lc};
//+
Line(1) = {1, 2};
Line(2) = {2, 5};
Line(3) = {1, 7};
Line(4) = {7, 5};
//+
Curve Loop(1) = {-3, -4, 2, 1};
Plane Surface(1) = {1};
//+
Transfinite Curve {2, 3} = 15 Using Progression 0.72;
Transfinite Curve {1, 4} = nx Using Progression 1;
Transfinite Surface {1};
Recombine Surface {1};
//+
Line(5) = {5, 6};
Line(6) = {7, 8};
Line(7) = {8, 6};
//+
Curve Loop(2) = {-7, 5, 4, -6};
Plane Surface(2) = {2};
//+
Transfinite Curve {5, 6} = 2 Using Progression 1.;
Transfinite Curve {7} = nx Using Progression 1;
//+
Line(8) = {8, 11};
Line(9) = {11, 9};
Line(10) = {6, 9};
//+
Curve Loop(3) = {-8, -9, 10, 7};
Plane Surface(3) = {3};
Transfinite Curve {8, 10} = 25 Using Bump 0.015;
Transfinite Curve {9} = nx Using Progression 1;
//+
Line(11) = {11, 12};
Line(12) = {12, 10};
Line(13) = {9, 10};
//+
Curve Loop(4) = {-12, 13, 9, -11};
Plane Surface(4) = {4};
//+
Transfinite Curve {11, 13} = 2 Using Progression 1.;
Transfinite Curve {12} = nx Using Progression 1;
//+
Line(14) = {12, 4};
Line(15) = {4, 3};
Line(16) = {10, 3};
//+
Curve Loop(5) = {-14, -15, 16, 12};
Plane Surface(5) = {5};
//+
Transfinite Curve {14, 16} = 15 Using Progression 1.35;
Transfinite Curve {15} = nx Using Progression 1;
//+
Transfinite Surface {1, 2, 3, 4, 5};
//+
Recombine Surface {1, 2, 3, 4};
Mesh.RecombineAll = 1;
//+
Physical Surface("ROCK", 201) = {1, 3, 5};
Physical Surface("FRACTURE", 101) = {2, 4};
//+
Coherence Mesh;
Mesh 2;
