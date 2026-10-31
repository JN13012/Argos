import {
  Component,
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import type { ReactNode } from "react";
import { Icon } from "../../../components/Icon";
import type { ScenePhase } from "./cycle";
import { GlobePoster } from "./GlobePoster";

const GlobeScene = lazy(() => import("./GlobeScene"));

const captions: Record<ScenePhase, string> = {
  osint: "OSINT · Explorer les connexions",
  red: "Red Team · Éprouver la résilience",
  blue: "Blue Team · Protéger l’environnement",
};

class SceneBoundary extends Component<
  { children: ReactNode; onFailure(): void },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onFailure();
  }
  render() {
    return this.state.failed ? <GlobePoster /> : this.props.children;
  }
}

export function IntelligenceScene() {
  const figureRef = useRef<HTMLElement>(null);
  const [supported, setSupported] = useState<boolean | null>(null);
  const [ready, setReady] = useState(false);
  const [phase, setPhase] = useState<ScenePhase>("osint");
  const [reducedMotion, setReducedMotion] = useState(
    () => window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  const [playing, setPlaying] = useState(
    () => !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  const [visible, setVisible] = useState(true);
  const [pageVisible, setPageVisible] = useState(
    () => document.visibilityState !== "hidden",
  );

  useEffect(() => {
    setSupported(typeof window.WebGL2RenderingContext !== "undefined");
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    function onMotionChange() {
      setReducedMotion(media.matches);
      if (media.matches) setPlaying(false);
    }
    function onVisibilityChange() {
      setPageVisible(document.visibilityState !== "hidden");
    }
    media.addEventListener("change", onMotionChange);
    document.addEventListener("visibilitychange", onVisibilityChange);
    const observer =
      typeof IntersectionObserver !== "undefined"
        ? new IntersectionObserver(
            ([entry]) => setVisible(entry?.isIntersecting ?? false),
            { threshold: 0.05 },
          )
        : null;
    if (figureRef.current) observer?.observe(figureRef.current);
    return () => {
      media.removeEventListener("change", onMotionChange);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      observer?.disconnect();
    };
  }, []);

  const onReady = useCallback(() => setReady(true), []);
  const onFailure = useCallback(() => {
    setSupported(false);
    setReady(false);
    setPlaying(false);
    setPhase("osint");
  }, []);
  const running = supported === true && playing && visible && pageVisible;

  return (
    <figure
      className={`intelligence-scene scene-phase--${phase}`}
      ref={figureRef}
      aria-label="L’univers Argos"
      data-scene-status={
        supported === false ? "fallback" : ready ? "ready" : "loading"
      }
      data-scene-playing={running ? "true" : "false"}
      data-scene-phase={phase}
    >
      <div
        className="scene-visual"
        role="img"
        aria-label="Globe de renseignement, accompagné successivement du Kraken rouge et du loup protecteur bleu"
      >
        {supported === true ? (
          <SceneBoundary onFailure={onFailure}>
            <Suspense fallback={<GlobePoster />}>
              <GlobeScene
                running={running}
                onPhase={setPhase}
                onReady={onReady}
                onFailure={onFailure}
              />
            </Suspense>
          </SceneBoundary>
        ) : (
          <GlobePoster />
        )}
      </div>
      <figcaption className="scene-caption">
        <span className="scene-caption-label">
          <span className="scene-caption-dot" />
          {captions[phase]}
        </span>
        <button
          type="button"
          className="scene-playback"
          disabled={supported !== true || !ready}
          aria-label={
            playing ? "Mettre l’animation en pause" : "Reprendre l’animation"
          }
          onClick={() => setPlaying((value) => !value)}
        >
          <Icon name={playing ? "pause" : "play"} />
          <span>
            {supported === false ? "Vue fixe" : playing ? "Pause" : "Animer"}
          </span>
        </button>
      </figcaption>
      {reducedMotion && (
        <span className="sr-only">
          Animation arrêtée selon votre préférence de réduction du mouvement.
        </span>
      )}
    </figure>
  );
}
