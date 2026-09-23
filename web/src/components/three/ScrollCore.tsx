"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import {
  Float,
  MeshDistortMaterial,
} from "@react-three/drei";

import {
  useEffect,
  useRef,
} from "react";

import type {
  ComponentRef,
} from "react";

import * as THREE from "three";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";


gsap.registerPlugin(ScrollTrigger);


// =========================================================
// COLOR PALETTE
// =========================================================

const COLORS = {
  hero: "#DDE8FF",
  drift: "#58E6FF",
  performance: "#9B7CFF",
  anomalies: "#FF70D2",
  rootCause: "#70FFD1",
};


// =========================================================
// CORE OBJECT
// =========================================================

function CoreObject() {

  const groupRef =
    useRef<THREE.Group>(null);


  const mainMeshRef =
    useRef<THREE.Mesh>(null);


  const ringOneRef =
    useRef<THREE.Mesh>(null);


  const ringTwoRef =
    useRef<THREE.Mesh>(null);


  const coreMaterialRef =
    useRef<ComponentRef<typeof MeshDistortMaterial>>(null);


  const wireMaterialRef =
    useRef<THREE.MeshBasicMaterial>(null);


  const ringOneMaterialRef =
    useRef<THREE.MeshBasicMaterial>(null);


  const ringTwoMaterialRef =
    useRef<THREE.MeshBasicMaterial>(null);



  // =======================================================
  // CONTINUOUS MOTION
  // =======================================================

  useFrame((state, delta) => {

    if (mainMeshRef.current) {

      mainMeshRef.current.rotation.y +=
        delta * 0.12;

      mainMeshRef.current.rotation.x +=
        delta * 0.05;
    }


    if (ringOneRef.current) {

      ringOneRef.current.rotation.z +=
        delta * 0.15;

      ringOneRef.current.rotation.x +=
        delta * 0.08;
    }


    if (ringTwoRef.current) {

      ringTwoRef.current.rotation.y -=
        delta * 0.12;

      ringTwoRef.current.rotation.z -=
        delta * 0.06;
    }


    // Very subtle pointer interaction
    if (groupRef.current) {

      groupRef.current.rotation.y +=
        state.pointer.x * 0.00035;

      groupRef.current.rotation.x +=
        state.pointer.y * 0.00025;
    }

  });



  // =======================================================
  // SCROLL ANIMATIONS
  // =======================================================

  useEffect(() => {

    if (
      !groupRef.current ||
      !coreMaterialRef.current ||
      !wireMaterialRef.current ||
      !ringOneMaterialRef.current ||
      !ringTwoMaterialRef.current
    ) {
      return;
    }


    const group =
      groupRef.current;


    const coreMaterial =
      coreMaterialRef.current;


    const wireMaterial =
      wireMaterialRef.current;


    const ringOneMaterial =
      ringOneMaterialRef.current;


    const ringTwoMaterial =
      ringTwoMaterialRef.current;


    const mm =
      gsap.matchMedia();



    // =====================================================
    // COLOR ANIMATION HELPER
    // =====================================================

    function animateColor(
      targetColor: THREE.Color,
      destination: string,
      trigger: string,
      start = "top 90%",
      end = "top 35%"
    ) {

      const newColor =
        new THREE.Color(
          destination
        );


      gsap.to(
        targetColor,
        {
          r: newColor.r,
          g: newColor.g,
          b: newColor.b,

          ease: "none",

          scrollTrigger: {
            trigger,
            start,
            end,
            scrub: 1.2,
          },
        }
      );

    }



    // =====================================================
    // DESKTOP
    // =====================================================

    mm.add(
      "(min-width: 768px)",
      () => {


        // -------------------------------------------------
        // INITIAL STATE
        // -------------------------------------------------

        gsap.set(
          group.position,
          {
            x: 0,
            y: -1.15,
            z: 0,
          }
        );


        gsap.set(
          group.scale,
          {
            x: 0.82,
            y: 0.82,
            z: 0.82,
          }
        );


        coreMaterial.color.set(
          COLORS.hero
        );


        wireMaterial.color.set(
          COLORS.hero
        );


        ringOneMaterial.color.set(
          COLORS.hero
        );


        ringTwoMaterial.color.set(
          COLORS.hero
        );



        // =================================================
        // HERO → DATA DRIFT
        //
        // Text left
        // Core right
        // Silver → Cyan
        // =================================================

        gsap.to(
          group.position,
          {
            x: 2.9,
            y: 0,
            z: 0,

            ease: "none",

            scrollTrigger: {
              trigger: "#drift",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.scale,
          {
            x: 0.9,
            y: 0.9,
            z: 0.9,

            ease: "none",

            scrollTrigger: {
              trigger: "#drift",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.rotation,
          {
            y: 1.4,
            z: 0.15,

            ease: "none",

            scrollTrigger: {
              trigger: "#drift",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        animateColor(
          coreMaterial.color,
          COLORS.drift,
          "#drift"
        );


        animateColor(
          wireMaterial.color,
          COLORS.drift,
          "#drift"
        );


        animateColor(
          ringOneMaterial.color,
          COLORS.drift,
          "#drift"
        );


        animateColor(
          ringTwoMaterial.color,
          COLORS.drift,
          "#drift"
        );



        // =================================================
        // DATA DRIFT → PERFORMANCE
        //
        // Text right
        // Core left
        // Cyan → Violet
        // =================================================

        gsap.to(
          group.position,
          {
            x: -2.9,
            y: 0.15,

            ease: "none",

            scrollTrigger: {
              trigger: "#performance",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.rotation,
          {
            y: 2.8,
            z: -0.2,

            ease: "none",

            scrollTrigger: {
              trigger: "#performance",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.scale,
          {
            x: 0.95,
            y: 0.95,
            z: 0.95,

            ease: "none",

            scrollTrigger: {
              trigger: "#performance",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        animateColor(
          coreMaterial.color,
          COLORS.performance,
          "#performance"
        );


        animateColor(
          wireMaterial.color,
          COLORS.performance,
          "#performance"
        );


        animateColor(
          ringOneMaterial.color,
          COLORS.performance,
          "#performance"
        );


        animateColor(
          ringTwoMaterial.color,
          COLORS.performance,
          "#performance"
        );



        // =================================================
        // PERFORMANCE → ANOMALIES
        //
        // Text left
        // Core right
        // Violet → Magenta
        // =================================================

        gsap.to(
          group.position,
          {
            x: 2.9,
            y: -0.1,

            ease: "none",

            scrollTrigger: {
              trigger: "#anomalies",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.rotation,
          {
            x: 0.6,
            y: 4.1,
            z: 0.2,

            ease: "none",

            scrollTrigger: {
              trigger: "#anomalies",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.scale,
          {
            x: 1,
            y: 1,
            z: 1,

            ease: "none",

            scrollTrigger: {
              trigger: "#anomalies",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        animateColor(
          coreMaterial.color,
          COLORS.anomalies,
          "#anomalies"
        );


        animateColor(
          wireMaterial.color,
          COLORS.anomalies,
          "#anomalies"
        );


        animateColor(
          ringOneMaterial.color,
          COLORS.anomalies,
          "#anomalies"
        );


        animateColor(
          ringTwoMaterial.color,
          COLORS.anomalies,
          "#anomalies"
        );



        // =================================================
        // ANOMALIES → ROOT CAUSE
        //
        // Text right
        // Core left
        // Magenta → Mint
        // =================================================

        gsap.to(
          group.position,
          {
            x: -2.8,
            y: 0,

            ease: "none",

            scrollTrigger: {
              trigger: "#root-cause",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.rotation,
          {
            x: 1,
            y: 5.3,
            z: -0.25,

            ease: "none",

            scrollTrigger: {
              trigger: "#root-cause",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.scale,
          {
            x: 1.08,
            y: 1.08,
            z: 1.08,

            ease: "none",

            scrollTrigger: {
              trigger: "#root-cause",
              start: "top 90%",
              end: "top 35%",
              scrub: 1,
            },
          }
        );


        animateColor(
          coreMaterial.color,
          COLORS.rootCause,
          "#root-cause"
        );


        animateColor(
          wireMaterial.color,
          COLORS.rootCause,
          "#root-cause"
        );


        animateColor(
          ringOneMaterial.color,
          COLORS.rootCause,
          "#root-cause"
        );


        animateColor(
          ringTwoMaterial.color,
          COLORS.rootCause,
          "#root-cause"
        );



        // =================================================
        // FINAL CTA
        // =================================================

        gsap.to(
          group.position,
          {
            x: 0,
            y: -0.5,

            ease: "none",

            scrollTrigger: {
              trigger: "#dashboard",
              start: "top 95%",
              end: "top 50%",
              scrub: 1,
            },
          }
        );


        gsap.to(
          group.scale,
          {
            x: 0.58,
            y: 0.58,
            z: 0.58,

            ease: "none",

            scrollTrigger: {
              trigger: "#dashboard",
              start: "top 95%",
              end: "top 50%",
              scrub: 1,
            },
          }
        );

      }
    );



    // =====================================================
    // MOBILE
    // =====================================================

    mm.add(
      "(max-width: 767px)",
      () => {

        gsap.set(
          group.position,
          {
            x: 0,
            y: -1.8,
            z: 0,
          }
        );


        gsap.set(
          group.scale,
          {
            x: 0.6,
            y: 0.6,
            z: 0.6,
          }
        );


        gsap.to(
          group.rotation,
          {
            y: Math.PI * 2,

            ease: "none",

            scrollTrigger: {
              trigger: "#hero",
              start: "top top",
              endTrigger: "#root-cause",
              end: "bottom bottom",
              scrub: 1,
            },
          }
        );


        animateColor(
          coreMaterial.color,
          COLORS.drift,
          "#drift"
        );


        animateColor(
          coreMaterial.color,
          COLORS.performance,
          "#performance"
        );


        animateColor(
          coreMaterial.color,
          COLORS.anomalies,
          "#anomalies"
        );


        animateColor(
          coreMaterial.color,
          COLORS.rootCause,
          "#root-cause"
        );

      }
    );


    ScrollTrigger.refresh();


    return () => {

      mm.revert();

    };

  }, []);



  // =======================================================
  // OBJECT
  // =======================================================

  return (
    <Float
      speed={1.7}
      rotationIntensity={0.2}
      floatIntensity={0.65}
    >

      <group
        ref={groupRef}
      >


        {/* MAIN CORE */}

        <mesh
          ref={mainMeshRef}
        >

          <icosahedronGeometry
            args={[
              1.75,
              10,
            ]}
          />


          <MeshDistortMaterial
            ref={coreMaterialRef}
            color={COLORS.hero}
            distort={0.32}
            speed={2}
            roughness={0.12}
            metalness={0.9}
          />

        </mesh>



        {/* OUTER WIREFRAME */}

        <mesh
          scale={1.2}
        >

          <icosahedronGeometry
            args={[
              1.75,
              3,
            ]}
          />


          <meshBasicMaterial
            ref={wireMaterialRef}
            color={COLORS.hero}
            wireframe
            transparent
            opacity={0.13}
          />

        </mesh>



        {/* ORBIT RING 1 */}

        <mesh
          ref={ringOneRef}
          rotation={[
            Math.PI / 2,
            0,
            0,
          ]}
        >

          <torusGeometry
            args={[
              2.35,
              0.012,
              16,
              200,
            ]}
          />


          <meshBasicMaterial
            ref={ringOneMaterialRef}
            color={COLORS.hero}
            transparent
            opacity={0.42}
          />

        </mesh>



        {/* ORBIT RING 2 */}

        <mesh
          ref={ringTwoRef}
          rotation={[
            0.8,
            0.4,
            0.3,
          ]}
        >

          <torusGeometry
            args={[
              2.65,
              0.008,
              16,
              200,
            ]}
          />


          <meshBasicMaterial
            ref={ringTwoMaterialRef}
            color={COLORS.hero}
            transparent
            opacity={0.22}
          />

        </mesh>


      </group>

    </Float>
  );
}



// =========================================================
// CANVAS
// =========================================================

export default function ScrollCore() {

  return (
    <div
      className="h-full w-full"
    >

      <Canvas
        camera={{
          position: [
            0,
            0,
            7,
          ],
          fov: 42,
        }}

        dpr={[
          1,
          1.6,
        ]}
      >

        <ambientLight
          intensity={1.05}
        />


        <directionalLight
          position={[
            5,
            5,
            6,
          ]}
          intensity={3.5}
        />


        <pointLight
          position={[
            -5,
            -3,
            4,
          ]}
          intensity={2}
          color="#8EBBFF"
        />


        <pointLight
          position={[
            4,
            -4,
            3,
          ]}
          intensity={1.7}
          color="#B97AFF"
        />


        <CoreObject />

      </Canvas>

    </div>
  );
}