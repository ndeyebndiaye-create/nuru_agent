--- Page 1 ---

Limites et continuité : rappels et compléments
Classe : Terminale S
1
Rappels
1.1
Limites
Limites à l’infini (définitions).
lim
x→+∞f(x) = +∞⇐⇒∀A > 0, ∃B > 0 : x ≥B ⇒f(x) ≥A,
lim
x→+∞f(x) = ℓ⇐⇒∀ε > 0, ∃A > 0 : x ≥A ⇒|f(x) −ℓ| ≤ε.
(Définitions analogues en −∞.)
Limites en x0.
lim
x→x+
0
f(x) = +∞⇐⇒∀A > 0, ∃α > 0 : x0 < x ≤x0 + α ⇒f(x) ≥A.
Théorème 1. Si f n’est pas définie en x0, alors f admet une limite en x0 si, et seulement si,
lim
x→x+
0
f(x) = lim
x→x−
0
f(x) = ℓ∈R.
1.2
Opérations sur les limites
Somme :
lim f
ℓ
ℓ
ℓ
+∞
−∞
+∞
lim g
ℓ′
+∞
−∞
+∞
−∞
−∞
lim(f + g)
ℓ+ ℓ′
+∞
−∞
+∞
−∞
F.I.
Produit :
lim f
ℓ
ℓ> 0
ℓ< 0
±∞
0
lim g
ℓ′
±∞
±∞
±∞
±∞
lim(f × g)
ℓℓ′
±∞
∓∞
(règle des signes)
F.I.
Quotient : lim f
g = ℓ
ℓ′ si ℓ′̸ = 0 ; les cas ∞
∞, ℓ
0, etc. se traitent par la règle des signes, sauf ∞
∞
et 0
0 qui sont indéterminés.
Remarque 1. Les quatre formes indéterminées sont :
∞−∞,
0 × ∞,
0
0,
∞
∞.
1.3
Levée d’une indétermination
Théorème 2. La limite à l’infini d’un polynôme est celle de son monôme de plus haut degré. La
limite à l’infini d’une fraction rationnelle est celle du quotient des monômes de plus haut degré.
On peut aussi factoriser par (x −x0), multiplier par l’expression conjuguée, ou utiliser les
théorèmes de comparaison.
1


--- Page 2 ---

Théorème 3 (Comparaison). Au voisinage de x0, si f(x) ≤g(x) : si lim f = +∞alors lim g =
+∞; si lim g = −∞alors lim f = −∞.
Théorème 4 (Théorème des gendarmes). Si g(x) ≤f(x) ≤h(x) au voisinage de x0 et lim
x→x0 g =
lim
x→x0 h = ℓ, alors lim
x→x0 f = ℓ.
Théorème 5 (Composée). Si lim
x→x0 f(x) = ℓ′ et lim
x→ℓ′ g(x) = ℓ, alors lim
x→x0 g ◦f(x) = ℓ.
2
Continuité
2.1
Définition
f est continue en x0 si lim
x→x0 f(x) = f(x0) (continuité à gauche et à droite avec limx→x−
0 f =
limx→x+
0 f = f(x0)).
2.2
Opérations
Si f est continue sur I et g sur J, alors f + g et fg sont continues sur I ∩J, et f
g est continue
là où g ne s’annule pas. La composée g ◦f (avec f(I) ⊂J) est continue sur I.
Remarque 2. Sont continues sur leur domaine : les fonctions polynômes (sur R), rationnelles,
√f, |f|, sin, cos, et tan sur R \ {π
2 + kπ}.
2.3
Prolongement par continuité
Si x0 /∈Df et lim
x→x0 f(x) = ℓ∈R, alors f est prolongeable par continuité en x0 par
f1(x) =
(
f(x)
si x̸ = x0
ℓ
si x = x0.
3
Compléments
3.1
Image d’un intervalle par une fonction continue
— L’image d’un intervalle I par une fonction continue est un intervalle J = f(I).
— L’image d’un intervalle fermé borné [a, b] est un intervalle fermé borné [α, β] avec α =
min[a,b] f et β = max[a,b] f.
Exercice d’application.
f est définie sur R∗par le tableau de variation :
x
−∞
−4
−3
0
1
2
+∞
f
−∞↗
2 ↘
−4 ↗
+∞∥+ ∞↘
0 ↗
4 ↘
0
Déterminer les images des intervalles indiqués.
Résolution.
f(] −∞; −4]) = ] −∞; 2],
f(] −∞; −3]) = ] −∞; 2],
f(] −∞; 0[) = R,
f([−4; −3]) = [−4; 2],
f([1; +∞[) = [0; 4],
f([−4; 0]) = [−4; +∞[,
f([0; +∞[) = [0; +∞[,
f(]0; 2]) = [0; +∞[.
2


--- Page 3 ---

3.2
Théorème des valeurs intermédiaires
Théorème 6. Si f est continue sur I et f(I) = J, alors pour tout y ∈J il existe au moins un
x0 ∈I tel que f(x0) = y.
Théorème 7 (Corollaire). Si f est continue sur [a, b] et f(a)×f(b) < 0, alors l’équation f(x) = 0
admet au moins une solution c ∈]a, b[.
Théorème 8 (Bijection). Si f est continue et strictement monotone sur I, alors f réalise une
bijection de I sur f(I) : pour tout y0 ∈f(I), il existe un unique x0 ∈I tel que f(x0) = y0.
Exercice d’application.
Soit f(x) = x3 −3x + 1. 1) Dresser le tableau de variation. 2) Déterminer le nombre de
solutions de f(x) = 0.
Résolution.
1) f′(x) = 3(x −1)(x + 1) ; f(−1) = 3, f(1) = −1, lim−∞f = −∞, lim+∞f = +∞.
x
−∞
−1
1
+∞
f′
+ 0 −
0 +
f
−∞↗
3
↘
−1
↗+∞
2) Sur ] −∞; −1], f(] −∞; −1]) = ] −∞; 3] ∋0 : une unique solution x0 < −1. Sur [−1; 1],
f(−1)f(1) = −3 < 0 : une unique solution x1 ∈]−1; 1[. Sur [1; +∞[, f bijective sur [−1; +∞[∋0 :
une unique solution x2 > 1. Donc f(x) = 0 admet trois solutions :
x0 < −1 < x1 < 1 < x2.
Cours d’après Sunudaara — Limites et continuité — Terminale S. Figures extraites automatiquement du
PDF source.
3