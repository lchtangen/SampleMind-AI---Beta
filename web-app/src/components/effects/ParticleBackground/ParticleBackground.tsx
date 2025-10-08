import { Engine } from "@tsparticles/engine";
import Particles from "@tsparticles/react";
import { FC, useCallback } from "react";
import { loadFull } from "tsparticles";
import { options } from "./particles-options";

export const ParticleBackground: FC = () => {
  const particlesInit = useCallback(async (engine: Engine) => {
    await loadFull(engine);
  }, []);

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={options}
      className="absolute top-0 left-0 w-full h-full z-0"
    />
  );
};
