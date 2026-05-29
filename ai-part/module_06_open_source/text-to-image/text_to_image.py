import torch
from diffusers import StableDiffusionXLPipeline


def main():
    # Το αναγνωριστικό (repository ID) του μοντέλου στο Hugging Face
    model_id = "segmind/SSD-1B"

    # Έλεγχος αν υπάρχει διαθέσιμη CUDA GPU
    # Αν επιστρέψει True, μπορούμε να εκμεταλλευτούμε την GPU για ταχύτερο inference
    # Αν επιστρέψει False, θα τρέξουμε το μοντέλο στην CPU, που είναι πιο αργή αλλά συμβατή με όλα τα συστήματα
    has_cuda = torch.cuda.is_available()

    # Φόρτωση του μοντέλου από το Hugging Face
    # - Αν υπάρχει GPU, χρησιμοποιούμε float16 για μικρότερη κατανάλωση μνήμης
    # - Αν δεν υπάρχει GPU, χρησιμοποιούμε float32 για καλύτερη συμβατότητα στην CPU
    # - use_safetensors=True για φόρτωση από ασφαλή μορφή weights
    pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if has_cuda else torch.float32,
        use_safetensors=True
    )

    if has_cuda:
        # Αν υπάρχει GPU:
        # Ενεργοποιούμε CPU offloading ώστε τμήματα του μοντέλου
        # να μεταφέρονται προσωρινά στην CPU όταν δεν χρησιμοποιούνται.
        # Αυτό βοηθά όταν η VRAM είναι περιορισμένη.
        pipe.enable_model_cpu_offload()

        # Δημιουργία generator στη GPU με σταθερό seed
        # ώστε να έχουμε αναπαραγώγιμα αποτελέσματα
        generator = torch.Generator("cuda").manual_seed(42)
    else:
        # Αν δεν υπάρχει GPU:
        # Μεταφέρουμε όλο το pipeline στην CPU
        pipe = pipe.to("cpu")

        # Δημιουργία generator στην CPU με σταθερό seed
        generator = torch.Generator("cpu").manual_seed(42)

    # Ζητάμε από τον χρήστη να εισάγει το prompt για τη δημιουργία της εικόνας
    prompt = input("Enter your prompt: ") 
    # Ζητάμε από τον χρήστη να εισάγει το όνομα της εξόδου εικόνας
    image_name = input("Enter the output image name (without extension): ") 
    

    image = pipe(
        prompt=prompt,
        height=768,
        width=768,
        num_inference_steps=25,
        guidance_scale=9.0, # Αυξάνουμε το guidance scale για πιο πιστή απόδοση του prompt
        negative_prompt="blurry, low quality, distorted, bad anatomy", # Προσθέτουμε αρνητικό prompt για να αποφύγουμε ανεπιθύμητα χαρακτηριστικά
        generator=generator # Χρήση του generator για αναπαραγώγιμα αποτελέσματα
    ).images[0] # Παίρνουμε την πρώτη εικόνα από τη λίστα αποτελεσμάτων

    # Αποθήκευση της εικόνας σε αρχείο PNG
    image.save(f"{image_name}.png")


if __name__ == "__main__":
    main()