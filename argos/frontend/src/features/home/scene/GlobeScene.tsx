import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import {
  BufferGeometry,
  CatmullRomCurve3,
  Color,
  ExtrudeGeometry,
  Float32BufferAttribute,
  Group,
  Mesh,
  MeshStandardMaterial,
  PointsMaterial,
  LineBasicMaterial,
  QuadraticBezierCurve3,
  Shape,
  TubeGeometry,
  Vector3,
} from "three";
import type { Material } from "three";
import outlines from "./land-outlines.json";
import { cycleAt } from "./cycle";
import type { ScenePhase } from "./cycle";

interface SceneProps {
  running: boolean;
  onPhase(phase: ScenePhase): void;
  onReady(): void;
  onFailure(): void;
}

function geographic(
  longitude: number,
  latitude: number,
  radius = 1.115,
): Vector3 {
  const phi = (latitude * Math.PI) / 180;
  const theta = (longitude * Math.PI) / 180;
  return new Vector3(
    Math.cos(phi) * Math.sin(theta),
    Math.sin(phi),
    Math.cos(phi) * Math.cos(theta),
  ).multiplyScalar(radius);
}

function segments(lines: Vector3[][]): BufferGeometry {
  const positions: number[] = [];
  for (const line of lines) {
    for (let index = 1; index < line.length; index++) {
      positions.push(...line[index - 1]!.toArray(), ...line[index]!.toArray());
    }
  }
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new Float32BufferAttribute(positions, 3));
  return geometry;
}

function prepareGlobe() {
  const landmarks = [
    [-74, 41],
    [-118, 34],
    [-99, 19],
    [-46, -24],
    [-58, -35],
    [-0.1, 51.5],
    [2.35, 48.85],
    [13.4, 52.5],
    [37.6, 55.7],
    [28, -26],
    [3.4, 6.5],
    [31.2, 30],
    [55.3, 25.2],
    [77.2, 28.6],
    [103.8, 1.3],
    [139.7, 35.7],
    [151.2, -33.9],
    [116.4, 39.9],
    [126.9, 37.5],
    [18.4, -34],
  ].map(([longitude, latitude]) => geographic(longitude!, latitude!, 1.13));
  const links = [
    [0, 5],
    [5, 6],
    [6, 11],
    [6, 13],
    [11, 12],
    [12, 14],
    [14, 15],
    [14, 16],
    [3, 10],
    [10, 19],
    [7, 17],
    [1, 15],
  ];
  const arcs = links.map(([start, end]) => {
    const a = landmarks[start!]!;
    const b = landmarks[end!]!;
    const midpoint = a.clone().add(b).normalize().multiplyScalar(1.5);
    return new QuadraticBezierCurve3(a, midpoint, b).getPoints(28);
  });
  const nodes = new BufferGeometry().setFromPoints(landmarks);
  const discoveries = new BufferGeometry().setFromPoints([
    landmarks[6]!,
    landmarks[12]!,
    landmarks[14]!,
  ]);
  const coasts = segments(
    outlines.map((line) =>
      line.map(([longitude, latitude]) => geographic(longitude!, latitude!)),
    ),
  );
  const network = segments(arcs);
  return { coasts, network, nodes, discoveries };
}

function wolfHead(): ExtrudeGeometry {
  const silhouette = new Shape();
  silhouette.moveTo(-0.52, 0.4);
  silhouette.lineTo(-0.7, 1.1);
  silhouette.lineTo(-0.16, 0.8);
  silhouette.lineTo(0, 0.88);
  silhouette.lineTo(0.16, 0.8);
  silhouette.lineTo(0.7, 1.1);
  silhouette.lineTo(0.52, 0.4);
  silhouette.lineTo(0.63, 0.02);
  silhouette.lineTo(0.4, -0.5);
  silhouette.lineTo(0, -0.8);
  silhouette.lineTo(-0.4, -0.5);
  silhouette.lineTo(-0.63, 0.02);
  silhouette.closePath();
  const geometry = new ExtrudeGeometry(silhouette, {
    depth: 0.2,
    bevelEnabled: true,
    bevelSegments: 1,
    steps: 1,
    bevelSize: 0.1,
    bevelThickness: 0.08,
  });
  geometry.center();
  return geometry;
}

function prepareTentacles(): TubeGeometry[] {
  const paths = [
    [
      [0, -0.15, 0],
      [0.55, -0.48, 0.12],
      [1.2, -0.65, 0.1],
      [1.75, -0.22, -0.02],
    ],
    [
      [-0.12, -0.2, 0.05],
      [0.22, -0.78, 0.15],
      [1.03, -1, -0.08],
      [1.66, -0.75, -0.15],
    ],
    [
      [0.18, -0.13, -0.12],
      [0.9, 0.23, -0.25],
      [1.25, 0.88, -0.38],
      [1.91, 1.04, -0.5],
    ],
    [
      [-0.2, -0.2, 0],
      [-0.55, -0.65, 0.1],
      [-0.22, -1.05, 0.12],
      [0.26, -0.9, 0],
    ],
    [
      [0.22, -0.2, 0],
      [0.55, -0.5, 0.4],
      [0.92, -0.07, 0.28],
      [1.17, 0.38, 0.06],
    ],
    [
      [-0.2, -0.1, -0.1],
      [-0.68, 0.05, -0.3],
      [-0.57, 0.68, -0.4],
      [0.23, 0.98, -0.35],
    ],
  ];
  return paths.map(
    (path, index) =>
      new TubeGeometry(
        new CatmullRomCurve3(path.map(([x, y, z]) => new Vector3(x, y, z))),
        28,
        index < 3 ? 0.045 : 0.032,
        5,
        false,
      ),
  );
}

function fadeMaterials(group: Group): Material[] {
  const materials = new Set<Material>();
  group.traverse((object) => {
    if (object instanceof Mesh) {
      const entries = Array.isArray(object.material)
        ? object.material
        : [object.material];
      for (const material of entries) {
        material.transparent = true;
        material.depthWrite = false;
        materials.add(material);
      }
    }
  });
  return [...materials];
}

function SceneContent({ running, onPhase, onReady, onFailure }: SceneProps) {
  const globe = useRef<Group>(null);
  const wolf = useRef<Group>(null);
  const kraken = useRef<Group>(null);
  const shield = useRef<Mesh>(null);
  const gold = useRef<PointsMaterial>(null);
  const halo = useRef<LineBasicMaterial>(null);
  const time = useRef(0);
  const lastPhase = useRef<ScenePhase>("osint");
  const announcedReady = useRef(false);
  const fading = useRef<{ wolf: Material[]; kraken: Material[] }>({
    wolf: [],
    kraken: [],
  });
  const { invalidate, gl } = useThree();
  const data = useMemo(prepareGlobe, []);
  const headGeometry = useMemo(wolfHead, []);
  const tentacles = useMemo(prepareTentacles, []);
  const metal = useMemo(
    () =>
      new MeshStandardMaterial({
        color: "#52687e",
        emissive: "#17314f",
        emissiveIntensity: 0.15,
        roughness: 0.48,
        metalness: 0.58,
        transparent: true,
        depthWrite: false,
      }),
    [],
  );
  const redMetal = useMemo(
    () =>
      new MeshStandardMaterial({
        color: "#624352",
        emissive: "#72283c",
        emissiveIntensity: 0.18,
        roughness: 0.46,
        metalness: 0.58,
        transparent: true,
        depthWrite: false,
      }),
    [],
  );
  const violet = useMemo(() => new Color("#b29adf"), []);
  const redColor = useMemo(() => new Color("#c86782"), []);
  const blueColor = useMemo(() => new Color("#6faaff"), []);

  useLayoutEffect(() => {
    if (wolf.current && kraken.current) {
      fading.current = {
        wolf: fadeMaterials(wolf.current),
        kraken: fadeMaterials(kraken.current),
      };
    }
    invalidate();
  }, [invalidate]);

  useEffect(() => {
    const canvas = gl.domElement;
    function onContextLoss(event: Event) {
      event.preventDefault();
      onFailure();
    }
    canvas.addEventListener("webglcontextlost", onContextLoss);
    return () => canvas.removeEventListener("webglcontextlost", onContextLoss);
  }, [gl, onFailure]);

  useEffect(() => {
    if (!running) {
      invalidate();
      return;
    }
    let stopped = false;
    let timeout: number;
    function requestFrame() {
      if (stopped) return;
      invalidate();
      timeout = window.setTimeout(requestFrame, 1000 / 30);
    }
    requestFrame();
    return () => {
      stopped = true;
      window.clearTimeout(timeout);
    };
  }, [running, invalidate]);

  useEffect(
    () => () => {
      for (const geometry of Object.values(data)) geometry.dispose();
      headGeometry.dispose();
      tentacles.forEach((geometry) => geometry.dispose());
      metal.dispose();
      redMetal.dispose();
    },
    [data, headGeometry, tentacles, metal, redMetal],
  );

  useFrame((_state, delta) => {
    if (running) time.current += Math.min(delta, 0.1);
    const current = cycleAt(time.current);
    if (!announcedReady.current) {
      announcedReady.current = true;
      onReady();
    }
    if (current.phase !== lastPhase.current) {
      lastPhase.current = current.phase;
      onPhase(current.phase);
    }
    if (globe.current) globe.current.rotation.y = 0.28 + time.current * 0.035;
    if (kraken.current) {
      kraken.current.visible = current.red > 0.001;
      kraken.current.position.x = -1.8 + current.red * 0.15;
      kraken.current.rotation.y = 0.12 + Math.sin(time.current * 0.2) * 0.035;
      for (const material of fading.current.kraken)
        material.opacity = current.red * 0.82;
    }
    if (wolf.current) {
      wolf.current.visible = current.blue > 0.001;
      wolf.current.rotation.y = -0.2 + Math.sin(time.current * 0.15) * 0.03;
      for (const material of fading.current.wolf)
        material.opacity = current.blue * 0.85;
    }
    if (shield.current) {
      shield.current.visible = current.blue > 0.001;
      shield.current.rotation.z = time.current * 0.1;
      (shield.current.material as Material).opacity =
        current.blue * (0.38 + Math.sin(time.current * 0.8) * 0.06);
    }
    if (gold.current)
      gold.current.opacity = 0.8 + Math.sin(time.current * 0.65) * 0.13;
    if (halo.current)
      halo.current.color
        .copy(violet)
        .lerp(redColor, current.red * 0.5)
        .lerp(blueColor, current.blue * 0.5);
  });

  return (
    <>
      <ambientLight intensity={1.1} />
      <directionalLight
        position={[2.5, 3, 4]}
        intensity={3.1}
        color="#c4d5ee"
      />
      <directionalLight position={[-3, 1, 2]} intensity={1.5} color="#ae97d8" />
      <group ref={globe} rotation={[0.13, 0.28, -0.08]}>
        <mesh>
          <sphereGeometry args={[1.1, 48, 32]} />
          <meshStandardMaterial
            color="#121d30"
            metalness={0.62}
            roughness={0.46}
          />
        </mesh>
        <mesh>
          <sphereGeometry args={[1.107, 24, 16]} />
          <meshBasicMaterial
            color="#9d8abf"
            wireframe
            transparent
            opacity={0.08}
            depthWrite={false}
          />
        </mesh>
        <lineSegments geometry={data.coasts}>
          <lineBasicMaterial color="#8b85b2" transparent opacity={0.66} />
        </lineSegments>
        <lineSegments geometry={data.network}>
          <lineBasicMaterial
            ref={halo}
            color="#b29adf"
            transparent
            opacity={0.42}
          />
        </lineSegments>
        <points geometry={data.nodes}>
          <pointsMaterial
            color="#baa0ff"
            size={0.036}
            sizeAttenuation
            transparent
            opacity={0.9}
          />
        </points>
        <points geometry={data.discoveries}>
          <pointsMaterial
            ref={gold}
            color="#f0c884"
            size={0.054}
            sizeAttenuation
            transparent
            opacity={0.9}
          />
        </points>
      </group>
      <mesh rotation={[1.06, 0.15, -0.34]}>
        <torusGeometry args={[1.47, 0.005, 5, 90]} />
        <meshBasicMaterial
          color="#8d75b9"
          transparent
          opacity={0.35}
          depthWrite={false}
        />
      </mesh>
      <mesh rotation={[0.3, 0.2, 0.5]}>
        <torusGeometry args={[1.25, 0.004, 5, 80]} />
        <meshBasicMaterial
          color="#71628e"
          transparent
          opacity={0.23}
          depthWrite={false}
        />
      </mesh>
      <group
        ref={kraken}
        position={[-1.8, 0.15, 0.05]}
        scale={0.86}
        visible={false}
      >
        <mesh
          material={redMetal}
          position={[0, 0.14, 0]}
          scale={[0.7, 1, 0.65]}
        >
          <icosahedronGeometry args={[0.51, 1]} />
        </mesh>
        <mesh material={redMetal} position={[0, 0.48, -0.07]}>
          <coneGeometry args={[0.36, 0.6, 6]} />
        </mesh>
        {[-0.18, 0.18].map((x) => (
          <mesh key={x} position={[x, 0.17, 0.29]} rotation={[0, 0, x * 1.5]}>
            <boxGeometry args={[0.14, 0.035, 0.035]} />
            <meshBasicMaterial color="#e28393" transparent depthWrite={false} />
          </mesh>
        ))}
        {tentacles.map((geometry, index) => (
          <mesh key={index} geometry={geometry} material={redMetal} />
        ))}
      </group>
      <group
        ref={wolf}
        position={[1.65, -0.08, 0.05]}
        scale={0.66}
        visible={false}
      >
        <mesh geometry={headGeometry} material={metal} />
        <mesh
          material={metal}
          position={[0, -0.24, 0.28]}
          rotation={[0.1, 0, 0]}
          scale={[0.8, 0.7, 1]}
        >
          <octahedronGeometry args={[0.45, 0]} />
        </mesh>
        <mesh
          material={metal}
          position={[0, -1, -0.15]}
          scale={[1.15, 0.65, 0.55]}
        >
          <dodecahedronGeometry args={[0.69, 0]} />
        </mesh>
        {[-0.31, 0.31].map((x) => (
          <mesh key={x} position={[x, 0.15, 0.22]} rotation={[0, 0, -x * 0.7]}>
            <boxGeometry args={[0.23, 0.045, 0.04]} />
            <meshBasicMaterial color="#79bbff" transparent depthWrite={false} />
          </mesh>
        ))}
        <mesh position={[0, -0.28, 0.59]}>
          <boxGeometry args={[0.12, 0.08, 0.09]} />
          <meshStandardMaterial
            color="#0d1420"
            transparent
            depthWrite={false}
          />
        </mesh>
      </group>
      <mesh
        ref={shield}
        rotation={[0.15, 0.3, 0]}
        position={[0, 0, 0.06]}
        visible={false}
      >
        <torusGeometry args={[1.35, 0.009, 5, 90]} />
        <meshBasicMaterial
          color="#75b3ff"
          transparent
          opacity={0}
          depthWrite={false}
        />
      </mesh>
    </>
  );
}

export default function GlobeScene(props: SceneProps) {
  const ratio = useMemo(() => {
    const memory = (navigator as Navigator & { deviceMemory?: number })
      .deviceMemory;
    return navigator.hardwareConcurrency <= 4 ||
      (memory !== undefined && memory <= 4)
      ? 1
      : Math.min(window.devicePixelRatio || 1, 1.35);
  }, []);
  return (
    <Canvas
      aria-hidden="true"
      frameloop="demand"
      dpr={ratio}
      camera={{ position: [0, 0.18, 5.1], fov: 37, near: 0.1, far: 20 }}
      gl={{ alpha: true, antialias: true, powerPreference: "low-power" }}
    >
      <SceneContent {...props} />
    </Canvas>
  );
}
