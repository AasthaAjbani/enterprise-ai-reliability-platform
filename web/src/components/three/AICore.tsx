"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import {
  Float,
  MeshDistortMaterial,
  OrbitControls,
} from "@react-three/drei";

import { useRef } from "react";

import type { Mesh } from "three";


function Core() {
  const meshRef = useRef<Mesh>(null);

  useFrame((state, delta) => {
    if (!meshRef.current) return;

    meshRef.current.rotation.x += delta * 0.12;
    meshRef.current.rotation.y += delta * 0.2;

    const mouseX = state.pointer.x;
    const mouseY = state.pointer.y;

    meshRef.current.rotation.y += mouseX * 0.002;
    meshRef.current.rotation.x += mouseY * 0.002;
  });

  return (
    <Float
      speed={2}
      rotationIntensity={0.7}
      floatIntensity={1.3}
    >
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2.15, 12]} />

        <MeshDistortMaterial
          distort={0.32}
          speed={2}
          roughness={0.15}
          metalness={0.8}
        />
      </mesh>
    </Float>
  );
}


export default function AICore() {
  return (
    <div className="absolute inset-0">
      <Canvas
        camera={{
          position: [0, 0, 7],
          fov: 40,
        }}
      >
        <ambientLight intensity={1.3} />

        <directionalLight
          position={[4, 4, 5]}
          intensity={4}
        />

        <pointLight
          position={[-4, -2, 3]}
          intensity={3}
        />

        <Core />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.35}
        />
      </Canvas>
    </div>
  );
}