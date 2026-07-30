--- Page 1 ---

Fonctions scalaires et vectorielles de Leibniz
Classe : Terminale S
1
Barycentre
Le barycentre G des points pondérés (Ai, αi)1≤i≤n (avec P αi̸ = 0) vérifie
n
X
i=1
αi
−−→
GAi =⃗0, et
−−→
OG =
1
P αi
n
X
i=1
αi
−−→
OAi,
zG =
P αizAi
P αi
.
Propriétés : homogénéité (G inchangé si on multiplie tous les poids par k̸ = 0) ; associativité
(on peut remplacer un sous-système par son barycentre partiel affecté de la somme des poids). Si
tous les poids sont égaux, G est l’isobarycentre (milieu pour deux points).
2
Produit scalaire
Avec⃗u = −−→
AB,⃗v = −→
AC :⃗
u ·⃗v = ∥⃗u∥∥⃗v∥cos(⃗u,⃗v) = AB × AH′ = xx′ + yy′,
où H′ est le projeté orthogonal de C sur (AB). Propriétés : symétrie, bilinéarité, et⃗u·⃗v = 0 ⇐⇒⃗
u ⊥⃗v (pour⃗u,⃗v̸ =⃗0).
2.1
Relation d’Al-Kashi
Pour un triangle ABC de côtés a, b, c opposés aux angles ˆA, ˆB, ˆC :
a2 = b2 + c2 −2bc cos ˆA,
sin ˆA
a
= sin ˆB
b
= sin ˆC
c
= 2S
abc,
S étant l’aire de ABC.
Figure 1 – Triangle ABC (côtés a, b, c) ; théorème de la médiane.
2.2
Théorème de la médiane
Si I est le milieu de [AB] :
−−→
MI = 1
2(−−→
MA + −−→
MB),
MA2 + MB2 = 2MI2 + AB2
2
.
Pour le centre de gravité G d’un triangle (I milieu de [BC]) : −→
AG = 2
3
−→
AI.
1


--- Page 2 ---

Figure 2 – Centre de gravité G et médiane AI (−→
AG = 2
3
−→
AI).
3
Fonction vectorielle de Leibniz⃗
f(M) =
n
X
i=1
αi
−−−→
MAi.
— si P αi = 0 :⃗f est constante,⃗f(M) =⃗f(O) ;
— si P αi̸ = 0 (barycentre G) :⃗f(M) =
X
αi
−−→
MG.
4
Fonction scalaire de Leibniz
f(M) =
n
X
i=1
αiMA2
i .
— si P αi = 0 : f(M) = f(O) + 2−−→
MO ·
X
αi
−−→
OAi (fonction affine) ;
— si P αi̸ = 0 (barycentre G) : f(M) =
X
αi

MG2 + f(G).
Exercice d’application.
ABC tel que AB = AC = 5, BC = 6. 1) Calculer −−→
AB·−→
AC. 2) G barycentre de (A, 2), (B, 3), (C, 3) :
calculer AG, puis avec f(M) = 2−−→
MB · −−→
MC + −−→
MA · (−−→
MC + −−→
MB), montrer f(M) = 4MG2 + f(G),
calculer f(A), f(G) et l’ensemble {M : f(M) = f(A)}.
Résolution.
1) Al-Kashi : cos ˆA = b2+c2−a2
2bc
, d’où −−→
AB · −→
AC = 25+25−36
2
= 7. 2) −→
AG = 3−→
AB+3−→
AC
8
donne
AG2 = 9, AG = 3. Le développement autour de G donne f(M) = 4MG2 + f(G). Avec f(A) =
2−−→
AB · −→
AC = 14 et f(G) = f(A) −4AG2 = −22 :
f(M) = f(A) ⇐⇒MG2 = 14 + 22
4
= 9 ⇐⇒MG = 3.
L’ensemble est le cercle de centre G et de rayon 3.
5
Surfaces et lignes de niveau
— {M :⃗u · −−→
MA = k} : droite (plan dans l’espace) perpendiculaire à⃗u ;
— {M : MA = MB} : médiatrice de [AB] (plan médiateur dans l’espace) ;
— {M : AM = k > 0} : cercle C(A, k) (sphère dans l’espace) ;
— {M : −−→
MA · −−→
MB = 0} : cercle de diamètre [AB] (sphère dans l’espace).
2


--- Page 3 ---

Figure 3 – Ensemble {M : f(M) = f(A)} : cercle de centre G, rayon 3.
Cours d’après Sunudaara — Fonctions scalaires et vectorielles de Leibniz — Seyni Ndiaye & Diny Faye.
Figures extraites automatiquement du PDF source.
3