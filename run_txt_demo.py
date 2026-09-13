import os
import shutil
import subprocess

def run_txt_test_case():
    test_dir = os.path.abspath("./txt_test_folder")
    
    # 1. Clean & create temporary test folder
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)

    print("==================================================")
    print(" REPOPILOT SETUP - TXT FILE TEST CASE DEMO ")
    print("==================================================")

    # 2. Copy the sample_test_case.txt into the folder as SETUP_INSTRUCTIONS.txt
    target_txt = os.path.join(test_dir, "SETUP_INSTRUCTIONS.txt")
    shutil.copy("sample_test_case.txt", target_txt)
    
    print("[+] Created text file test case: SETUP_INSTRUCTIONS.txt")
    print("\n--- File Contents (first 10 lines): ---")
    with open(target_txt, "r") as f:
        for i in range(10):
            print("  | " + f.readline().strip())

    print("\n--- Running `repopilot setup --dir ./txt_test_folder --dry-run` ---\n")

    # 3. Run repopilot setup command on the folder containing the txt file
    result = subprocess.run(
        ["repopilot", "setup", "--dir", test_dir, "--dry-run"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # 4. Clean up
    shutil.rmtree(test_dir)
    print("==================================================")
    print(" TEST COMPLETED ")
    print("==================================================")

if __name__ == "__main__":
    run_txt_test_case()
