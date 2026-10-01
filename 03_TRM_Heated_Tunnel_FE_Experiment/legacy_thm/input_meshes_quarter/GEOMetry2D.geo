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
R = 2.48 * unit;
r = 1.05;
# lc = 0.25 * unit;
lc = 0.65 * unit;
//+ Points
Point(1) = {-L, 0, 0, lc};
Point(2) = {-R, 0, 0, lc};
Point(3) = {-r, 0, 0, lc};
Point(4) = { 0, 0, 0, lc};
Point(5) = { r, 0, 0, lc};
Point(6) = { R, 0, 0, lc};
Point(7) = { L, 0, 0, lc};
Point(8) = { L, H, 0, lc};
Point(9) = { 0, H, 0, lc};
Point(10) = {-L, H,  0, lc};
Point(11) = { 0, R,  0, lc};
Point(12) = { 0, r, 0, lc};
//+ Lines
Line(1) = {1,2};
Line(2) = {2,3};
Line(4) = {5,6};
Line(5) = {6,7};
Line(6) = {7,8};
Line(7) = {8,9};
Line(8) = {9,10};
Line(9) = {10,1};
//+
Circle(10) = {2, 4, 11};
Circle(11) = {6, 4, 11};
Circle(12) = {3, 4, 12};
Circle(13) = {5, 4, 12};
//+
Line(14) = {11, 9};
Line(15) = {11, 12};
//+
Curve Loop(1) = {9, 1, 10, 14, 8};
Plane Surface(1) = {1};
//+
Curve Loop(2) = {2, 12, -15, -10};
Plane Surface(2) = {2};
//+
Curve Loop(3) = {-14, 7, 6, 5, -11};
Plane Surface(3) = {3};
//+
Curve Loop(4) = {4, 11, 15, -13};
Plane Surface(4) = {4};
//+
// Transfinite Curve {2, 4, 10, 11, 12, 13, 15} = 35 Using Progression 1;
// Transfinite Curve {1, 5, 6, 7, 8, 9, 14} = 35 Using Progression 1;
//+
// Transfinite Surface {2};
// Recombine Surface {2};
// Transfinite Surface {4};
// Recombine Surface {4};
//+
// Physical Surface("tunnel", 100) = {1,2,3,4};
Physical Surface(101) = {2,4};
Physical Surface(102) = {1,3};
Physical Point("pt0") = {1};
Physical Curve("bottom") = {1, 2, 4, 5};
Physical Curve("left") = {9};
Physical Curve("right") = {6};
Physical Curve("top") = {7,8};
Physical Curve("arc") = {12,13};
//+
Mesh.Algorithm = 1;
Mesh.ElementOrder = 2;
Mesh 2;