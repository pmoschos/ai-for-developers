# Βήμα 4: Συμπεράσματα

## 4a. Ασαφές vs Συγκεκριμένο prompt

Παρατήρησα ότι με το ασαφές prompt "a sort function" το μοντέλο επέλεξε τη πιο εύκολη λύση — απλά κάλεσε τη built-in sorted() χωρίς να υλοποιήσει δικό του αλγόριθμο. Αντίθετα, με το συγκεκριμένο prompt "quicksort with in-place partitioning for a list of integers" παρήγαγε πλήρη υλοποίηση με partition function, pivot selection και recursion. Το συμπέρασμα είναι ξεκάθαρο: αν δεν περιγράψεις ακριβώς τι θέλεις, το μοντέλο θα πάρει τον εύκολο δρόμο.

## 4b. Temperature 0.2 vs 0.9

Τρέχοντας δύο φορές με temperature 0.9 πήρα διαφορετικά variable names κάθε φορά (π.χ. find_prime_numbers_up_to vs find_primes_up_to) και μικροδιαφορές στα edge case checks. Με temperature 0.2 τα αποτελέσματα ήταν σχεδόν ίδια μεταξύ εκτελέσεων. Για code generation δεν χρειαζόμαστε δημιουργικότητα — χρειαζόμαστε σωστό, σταθερό κώδικα, γι' αυτό η χαμηλή temperature είναι η σωστή επιλογή.
