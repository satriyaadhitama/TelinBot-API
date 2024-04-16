import csv
import warnings

def seed_data_from_csv(csv_file, model):
    with open(csv_file, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            obj_data = {
                field.name: row[field.name]
                for field in model._meta.fields
                if field.name in row
            }
            obj = model.objects.create(**obj_data)
            obj.save()
