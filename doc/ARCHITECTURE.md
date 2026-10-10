# Argos — Architecture minimale

## Architecture actuelle

**No active application implementation yet.** Le dépôt contient le README et
la documentation de direction ; aucun package applicatif, test fonctionnel ou
workflow de CI n'est actif.

La prochaine fondation sera construite sous :

```text
argos/
└── osint/
```

Ces fichiers seront créés dans la prochaine tâche. Cette passe ne crée aucun
package, contrat de données ni implémentation.

## Direction future

Les domaines Red, Defense et Agents, ainsi qu'une interface utilisateur,
n'auront leurs dossiers que lorsqu'ils seront réellement développés.
Une API ou un noyau partagé nécessitera également un besoin démontré.
L'Interface représente l'UX du produit et n'impose pas un package Python.

## Capacités et orchestration

```text
Capability = ce qu'Argos sait faire
Workflow   = assemblage de capacités
Harness    = pilotage/orchestration par un agent
```

Les capacités métier devront rester utilisables sans agent. Un workflow les
assemblera ; un futur harness pourra piloter leur exécution et appliquer ses
permissions. L'interface présentera les recherches et leurs résultats.

L'[architecture OSINT](OSINT.md) porte les principes du premier moteur.
Le code futur vivra sous `argos/` ; `.argos/`, ignoré par Git, accueillera les
données runtime locales. Aucun arbre de stockage n'est créé maintenant.
