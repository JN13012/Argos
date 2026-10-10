# Argos — Cadre du projet

**Status: CANONICAL — contexte académique et règles d'usage validés.**

## Contexte

Argos est un projet de fin d'études du cursus Epitech, en 4e année, spécialité
cybersécurité. Il est encadré et évalué par l'équipe pédagogique d'Epitech
Marseille.

Sa finalité est pédagogique et démonstrative : construire une plateforme OSINT
complète, puis des modules Red et Defense, en appliquant les pratiques
professionnelles du métier. Ces pratiques couvrent l'autorisation, le périmètre,
la traçabilité, la conformité juridique et la preuve.

## OSINT

- Les sources utilisées sont publiques ou accessibles légalement. Les API
  officielles et l'open data passent en premier.
- L'outil respecte les conditions d'utilisation des plateformes, `robots.txt`
  et les limites de débit. Son User-Agent est identifié.
- **Aucun contournement de mesure technique** : authentification, CAPTCHA,
  blocage d'adresse IP, paywall ou faux comptes.
- Les organisations, c'est-à-dire les entreprises et leurs établissements, sont
  les entités prioritaires.
- Les données de personnes physiques suivent le RGPD : finalité définie,
  minimisation, durée de conservation et droit d'opposition. Cela inclut les
  entrepreneurs individuels. Aucun profilage de particuliers n'est réalisé.
- L'outil n'automatise aucune prise de contact.

Les conditions propres à chaque famille de sources sont décrites dans
l'[architecture OSINT](../architecture/OSINT.md#sources-et-conditions-de-collecte).

## Red

- Les actions actives visent uniquement des cibles explicitement autorisées :
  - laboratoires de l'équipe : VM, conteneurs, GOAD, DVWA, Juice Shop ou équivalents ;
  - plateformes d'entraînement, selon leurs règles ;
  - cible tierce, avec une autorisation écrite et un périmètre défini.
- L'outil vérifie le périmètre autorisé avant toute action active et en garde
  une trace.
- Aucun scan de masse sur Internet, aucun déni de service et aucune charge
  destructive en dehors du laboratoire.

## Defense

Les journaux, la télémétrie et les échantillons proviennent des laboratoires de
l'équipe ou de jeux de données publics.

## Portée

Ce cadre décrit l'usage prévu d'Argos. Il ne vaut pas autorisation de tester une
cible réelle. Les assistants de développement IA travaillent dans ce cadre : leur
travail offensif porte sur les laboratoires, les plateformes d'entraînement ou
des données synthétiques.
