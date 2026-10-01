// parameter visualization
Geometry.PointNumbers = 1;
Geometry.LineNumbers = 1;
Geometry.SurfaceNumbers = 1;
Geometry.VolumeNumbers = 1;
Geometry.Color.Points = Red;
Geometry.Color.Lines = Blue;
Geometry.Color.Surfaces = Green;
Geometry.Color.Volumes = Gold;
General.Color.Text = Black;
//+ Parameters
unit = 1.; // 
L = 25 * unit;
H = 25 * unit;
R = 1.24 * unit;
r = 0.525 * unit;
// r = 1.05;
// lc = 0.25 * unit;
lc = 0.65 * unit;
//+ Points
Point(1) = { 0, 0, 0, lc};
Point(2) = { r, 0, 0, lc};
Point(3) = { R, 0, 0, lc};
Point(4) = { L, 0, 0, lc};
Point(5) = { L, H, 0, lc};
Point(6) = { 0, H, 0, lc};
Point(7) = { 0, R,  0, lc};
Point(8) = { 0, r, 0, lc};
//+ Lines
Line(1) = {2,3};
Line(2) = {3,4};
Line(3) = {4,5};
Line(4) = {5,6};
//+
Circle(7) = {3, 1, 7};
Circle(8) = {2, 1, 8};
//+
Line(5) = {7, 6};
Line(6) = {7, 8};
//+
Curve Loop(1) = {6, -8, 1, 7};
Plane Surface(1) = {1};
//+
Curve Loop(2) = {-5, 4, 3, 2, -7};
Plane Surface(2) = {2};
// //+
// // Transfinite Curve {2, 4, 10, 11, 12, 13, 15} = 35 Using Progression 1;
// // Transfinite Curve {1, 5, 6, 7, 8, 9, 14} = 35 Using Progression 1;
// //+
// // Transfinite Surface {2};
// // Recombine Surface {2};
// // Transfinite Surface {4};
// // Recombine Surface {4};
// //+
// Physical Surface("tunnel", 100) = {1,2,3,4};
Physical Surface(101) = {1};
Physical Surface(102) = {2};
Physical Point("pt0") = {4};
Physical Curve("bottom") = {1, 2};
Physical Curve("left") = {5,6};
Physical Curve("right") = {3};
Physical Curve("top") = {4};
Physical Curve("arc_inner") = {8};
Physical Curve("arc_outer") = {7};
// //+
Mesh.Algorithm = 1;
Mesh.ElementOrder = 2;
Mesh 2;//+


