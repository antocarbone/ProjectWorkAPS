from solcx import compile_source, install_solc
import json
import os
import sys

def compile_contracts_in_directory(input_dir, output_root_dir='./build'):
    if not os.path.exists(input_dir):
        print(f"Errore: La directory di input '{input_dir}' non esiste.")
        return

    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
        print(f"Creata directory di output principale: {output_root_dir}")

    solidity_files = [f for f in os.listdir(input_dir) if f.endswith('.sol')]

    if not solidity_files:
        print(f"Nessun file .sol trovato nella directory '{input_dir}'.")
        return

    print(f"Trovati {len(solidity_files)} file Solidity in '{input_dir}'.")
    
    install_solc('0.8.0')
    
    for sol_file_name in solidity_files:
        sol_file_path = os.path.join(input_dir, sol_file_name)

        try:
            with open(sol_file_path, 'r') as f:
                solidity_code = f.read()
            print(f"\nCaricato codice Solidity da: {sol_file_path}")
        except Exception as e:
            print(f"Errore nella lettura del file '{sol_file_path}': {e}. Salto la compilazione.")
            continue

        print(f"Compilazione del contratto da '{sol_file_name}'...")

        try:
            compiled_sol = compile_source(
                solidity_code,
                output_values=['abi', 'bin'],
                solc_version="0.8.0"
            )
            print("Compilazione completata con successo.")
        except Exception as e:
            print(f"Errore durante la compilazione di '{sol_file_path}': {e}")
            print("Assicurati che 'solcx' sia installato e che la versione di solc sia disponibile.")
            continue

        for contract_id, contract_interface in compiled_sol.items():
            full_contract_name = contract_id.split(':')[-1]
            print(f"Contratto rilevato: {full_contract_name}")

            contract_output_dir = os.path.join(output_root_dir, full_contract_name)
            if not os.path.exists(contract_output_dir):
                os.makedirs(contract_output_dir)
                print(f"Creata sottocartella per '{full_contract_name}': {contract_output_dir}")

            bytecode = contract_interface['bin']
            abi = contract_interface['abi']

            bytecode_output_path = os.path.join(contract_output_dir, f'{full_contract_name}.bin')
            with open(bytecode_output_path, 'w') as f:
                f.write(bytecode)
            print(f"Bytecode salvato in: {bytecode_output_path}")

            abi_output_path = os.path.join(contract_output_dir, f'{full_contract_name}.json')
            with open(abi_output_path, 'w') as f:
                json.dump(abi, f, indent=4)
            print(f"ABI salvato in: {abi_output_path}")

if __name__ == '__main__':

    solidity_source_directory = './'

    print(f"Inizio compilazione dei contratti dalla directory: {solidity_source_directory}")
    compile_contracts_in_directory(solidity_source_directory)
    print("\nProcesso di compilazione completato.")
    print(f"Puoi trovare i file compilati nella cartella './build' (o quella specificata).")
    print("Ogni contratto avrà la sua sottocartella con ABI e Bytecode.")
