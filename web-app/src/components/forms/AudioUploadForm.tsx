import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { AudioFile, AudioFileSchema } from "../../schemas/audioFile";
import { useAudioStore } from "../../stores/audioStore";

export const AudioUploadForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<AudioFile>({
    resolver: zodResolver(AudioFileSchema),
  });
  const { loadTrack } = useAudioStore((state) => state.actions);

  const onSubmit = (data: AudioFile) => {
    console.log("Validated data:", data);
    if (data.audioFile) {
      // Mock duration for now
      loadTrack(data.audioFile.name, 240);
    }
    reset();
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="glass-card p-8 rounded-2xl space-y-6"
    >
      <div>
        <label
          htmlFor="audioFile"
          className="block text-lg font-heading text-glow-cyan mb-2"
        >
          Upload Audio File
        </label>
        <input
          id="audioFile"
          type="file"
          accept="audio/*"
          className="cyberpunk-input w-full"
          {...register("audioFile")}
        />
        {errors.audioFile && (
          <p className="text-red-500 mt-2">
            {errors.audioFile.message as string}
          </p>
        )}
      </div>
      <button type="submit" className="cyberpunk-button hover-glow-purple">
        Upload
      </button>
    </form>
  );
};
