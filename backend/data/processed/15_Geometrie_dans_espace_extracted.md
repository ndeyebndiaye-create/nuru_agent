--- Page 1 ---

Géométrie dans l’espace
Classe : Terminale S
1
Détermination de droites et de plans
Une droite ∆est déterminée par un point et un vecteur directeur : pour A, B, M ∈(AB) ⇐⇒
∃k, −−→
AM = k−−→
AB, ce qui donne une représentation paramétrique, puis cartésienne (intersection
de deux plans).
Un plan (P) est déterminé par trois points non alignés (ou un point et deux vecteurs). M ∈
(ABC) ⇐⇒∃k, k′, −−→
AM = k−−→
AB + k′−→
AC (équation paramétrique), d’où une équation cartésienne
ax + by + cz + d = 0.
Remarque 1. Pour un plan ax + by + cz + d = 0, le vecteur⃗n(a, b, c) est un vecteur normal.
2
Positions relatives
Deux droites sont coplanaires ou non. Une droite et un plan sont sécants (la droite perce le
plan) ou parallèles (∆∩P = ∅ou ∆⊂P). Deux plans sont parallèles (P = P ′ ou P ∩P ′ = ∅) ou
sécants selon une droite.
3
Parallélisme et orthogonalité
— Deux plans sont parallèles ssi leurs vecteurs normaux⃗n,⃗n′ sont colinéaires.
— Une droite ∆est perpendiculaire à un plan P ssi elle est perpendiculaire à deux droites
sécantes de P, ssi son vecteur directeur et⃗n sont colinéaires.
— Deux plans sont perpendiculaires ssi⃗n ⊥⃗n′.
4
Produit vectoriel
4.1
Définition
Le produit vectoriel⃗u ∧⃗v est le vecteur :
— nul si⃗u,⃗v sont colinéaires ;
— sinon perpendiculaire à⃗u et⃗v, tel que (⃗u,⃗v,⃗u ∧⃗v) soit direct et
∥⃗u ∧⃗v∥= ∥⃗u∥∥⃗v∥| sin(⃗u,⃗v)|.
4.2
Propriétés⃗
u ∧⃗v = −⃗v ∧⃗u,
(α⃗u) ∧⃗v = α(⃗u ∧⃗v),⃗
u ∧(⃗v +⃗w) =⃗u ∧⃗v +⃗u ∧⃗w.
4.3
Expression en base orthonormée directe
Avec⃗ı ∧⃗ȷ =⃗k,⃗ȷ ∧⃗k =⃗ı,⃗k ∧⃗ı =⃗ȷ :⃗
u
 xy
z

∧⃗v
 x′
y′
z′

=⃗ı

y
y′
z
z′
 −⃗ȷ

x
x′
z
z′
 +⃗k

x
x′
y
y′
 =
 yz′−zy′
zx′−xz′
xy′−yx′

.
1


--- Page 2 ---

Figure 1 – Repère direct ; aire du parallélogramme ABCD.
4.4
Applications
Aires :
AABD = 1
2
−−→
AB ∧−−→
AD
,
AABCD =
−−→
AB ∧−−→
AD
.
Distance d’un point à un plan P : ax + by + cz + d = 0 :
d(M0, P) = |ax0 + by0 + cz0 + d|
√
a2 + b2 + c2
.
Distance d’un point à une droite ∆(point A, directeur⃗u) :
d(M0, ∆) =
−−−→
M0A ∧⃗u

∥⃗u∥
.
Figure 2 – Distance d’un point à un plan et à une droite.
5
Produit mixte
Le produit mixte de⃗u,⃗v,⃗w est le réel⃗u · (⃗v ∧⃗w). En base orthonormée :⃗
u · (⃗v ∧⃗w) =

x
x′
x′′
y
y′
y′′
z
z′
z′′

.
Application : le volume du tétraèdre ABCD est
VABCD = 1
6
−−→
AD · (−−→
AB ∧−→
AC)
.
Cours d’après Sunudaara — Géométrie dans l’espace — Seyni Ndiaye & Diny Faye. Figures extraites
automatiquement du PDF source.
2