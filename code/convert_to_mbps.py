import csv
import os

def convert_to_mbps(value, unit):
    if not value or value == '':
        return ''
    try:
        value = float(value)
        if unit == 'Gbps':
            return value * 1000
        elif unit == 'Tbps':
            return value * 1000000
        elif unit == 'Kbps':
            return value / 1000
        else:  # Mbps ou desconhecido
            return value
    except ValueError:
        return ''  # Retorna uma string vazia se não puder converter

def process_csv(input_file, output_file):
    fields_to_convert = ['Input_Maximum', 'Input_Average', 'Input_Current',
                         'Output_Maximum', 'Output_Average', 'Output_Current']

    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = [field for field in reader.fieldnames if not field.endswith('_Unit')]
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            for field in fields_to_convert:
                if field in row and f"{field}_Unit" in row:
                    row[field] = convert_to_mbps(row[field], row[f"{field}_Unit"])
            
            # Remove os campos '_Unit'
            row = {k: v for k, v in row.items() if not k.endswith('_Unit')}
            writer.writerow(row)

def main():
    input_file = 'output/ix-br_slugs_data_processed.csv'
    output_file = 'output/ix-br_slugs_data_converted.csv'

    if not os.path.exists(input_file):
        print(f"Arquivo de entrada não encontrado: {input_file}")
        return

    process_csv(input_file, output_file)
    print(f"Conversão concluída. Arquivo de saída: {output_file}")

if __name__ == '__main__':
    main()
