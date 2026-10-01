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
fracT =  0.501;
fracB =  0.5;
lc = 1;

// ----------------------------
// Corner and split points
Point(1) = {0.1,         0.,          0., lc};
Point(2) = {cube_width,  0.,          0., lc};
Point(3) = {cube_width,  cube_height, 0., lc};
Point(4) = {0.1,         cube_height, 0., lc};
//+
Point(5) = {cube_width,  fracB,       0., lc};
Point(6) = {cube_width,  fracT,       0., lc};
//+
Point(7) = {0.1,         fracB,       0., lc};
Point(8) = {0.1,         fracT,       0., lc};
//+
Line(1) = {1, 2};
Line(2) = {2, 5};
Line(3) = {1, 7};
Line(4) = {7, 5};
//+
Curve Loop(1) = {-3,-4, 2, 1};
Surface(1) = {1};
//+
nx = 40;
Transfinite Curve {3, 2} = 30 Using Progression 0.87;
Transfinite Curve {1, 4} = nx Using Progression 1.;
Transfinite Surface{1};
//+
Line(5) = {5, 6};
Line(6) = {7, 8};
Line(7) = {8, 6};
//+
Curve Loop(2) = {-6, -7, 5, 4};
Plane Surface(2) = {2};
//+
Transfinite Curve {5, 6} = 1 Using Progression 1;
Transfinite Curve {7} = nx Using Progression 1.;
//+
Line(8) = {6, 3};
Line(9) = {8, 4};
Line(10) = {4, 3};
//+
Curve Loop(3) = {-9, -10, 8, 7};
Plane Surface(3) = {3};
//+
Transfinite Curve {8, 9} = 30 Using Progression 1.15;
Transfinite Curve {10} = nx Using Progression 1.;
//+
Transfinite Surface {1, 2, 3};
Recombine Surface{1, 2, 3};
//+
Physical Surface("ROCK", 201) = {1, 3};
Physical Surface("FRACTURE", 101) = {2};
//+
Mesh.RecombineAll = 1;
Coherence Mesh;
Mesh 2;
