import Navbar from "@/components/Navbar";
import SmoothScroll from "@/components/SmoothScroll";
import ScrollExperience from "@/components/sections/ScrollExperience";


export default function Home() {
  return (
    <main className="bg-[#080808]">

      <SmoothScroll />

      <Navbar />

      <ScrollExperience />

    </main>
  );
}