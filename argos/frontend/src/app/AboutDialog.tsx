import { Button } from "../components/Button";
import { Icon } from "../components/Icon";
import { Modal } from "../components/Modal";

export function AboutDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose(): void;
}) {
  return (
    <Modal
      id="about-dialog"
      open={open}
      onClose={onClose}
      title="À propos de cet espace"
      eyebrow="ARGOS / ESPACE LOCAL"
      closeLabel="Fermer les informations"
      className="about-dialog"
    >
      <p>
        Cet espace présente un dossier de mission, ses constats à examiner et
        son rapport.
      </p>
      <p>
        Les logs affichent les événements de cette session dans le navigateur.
        Ils ne constituent pas un journal d’audit persistant du harness.
      </p>
      <p>
        Argos Chat fournit des réponses locales à partir du dossier affiché.
        Aucun modèle IA ni moteur d’analyse n’est connecté à cette interface.
      </p>
      <Button variant="primary" onClick={onClose}>
        Revenir à l’accueil <Icon name="arrow" />
      </Button>
    </Modal>
  );
}
