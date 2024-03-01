from sqlalchemy import create_engine
import pandas as pd

class User(object):
    def __init__(self):
        self.CompanyId = 0
        self.CenterId = 0
        self.Name = ""

class Supply(object):
    def __init__(self):
        self.SupplyId = 0
        self.Name = ""
        self.UnitId = 0
        self.UnitName = ""
        self.UnitSymbol = ""

def connectionToDB():
    user = "root"
    password = "KNUi$#x8d=$0"
    host = "localhost"
    port = 3306
    schema = "tamboapp"

    # Connect to the database
    conn_str = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(
        user, password, host, port, schema)
    db = create_engine(conn_str, encoding='utf8')
    return db.raw_connection()

def dataList(storedProcedure, params):
    connection = connectionToDB()
 
    try:
        cursor = connection.cursor()
        cursor.callproc(storedProcedure, params)
        # fetch result parameters
        column_names_list = [x[0] for x in cursor.description]

        # construct a list of dict objects (<one table row>=<one dict>) 
        results = [dict(zip(column_names_list, row)) for row in cursor.fetchall()]

        cursor.close()
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close() 

    return results

def login(username, password):
    # set your parameters for the database
    results = dataList("pa_usuario_acceder", [username, password])
    user = User()
    if (len(results) > 0):
        user.CompanyId = results[0]['tm_idempresa']
        user.CenterId = results[0]['tm_idcentro']
        user.Name = results[0]['tm_nombres']
    return user

def getAllSupplies(companyId, centerId):
    results = dataList("pa_insumo_listar", ['1', companyId, centerId, 0, "", 0])
    supplies = []
    
    for item in results:
        supply = Supply()
        supply.SupplyId = item.get("tm_idinsumo")
        supply.Name = item.get("tm_nombre")
        supply.UnitId = item.get("tm_idunidadmedida")
        supply.UnitName = item.get("nombre_unidad")
        supply.UnitSymbol = item.get("simbolo_unidad")
        
        supplies.append(vars(supply))

    return supplies

def updateNutritionalValuesInSupplies():
    connection = connectionToDB()
    excel_file_path = 'nutritional_values.xlsx'  # Replace with your actual file path
    df = pd.read_excel(excel_file_path)

    try:
        cursor = connection.cursor()
        for index, row in df.iterrows():
            # Access row values by column name
            nameSupply = row['Ingrediente']
            calories = row['Calorías']
            fats = row["Grasas (g)"]
            carbohydrates = row["Carbohidratos (g)"]
            proteins = row["Proteínas (g)"]


            query = "UPDATE tm_insumo SET td_calorias = {0}, td_grasas = {1}, td_carbohidratos = {2}, td_proteinas = {3} WHERE tm_nombre = '{4}';".format(calories, fats, carbohydrates, proteins, nameSupply)
            cursor.execute(query)
            # Print the values, separated by commas
            print(nameSupply, ",", calories, ",", fats, ",", carbohydrates, ",", proteins)

        cursor.close()
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close() 

username = "Admin"
password = "GlobalMem369"
#
user = login(username, password)
supplies = getAllSupplies(user.CompanyId, user.CenterId)
#
#df = pd.DataFrame(supplies)
#df.to_excel('supplies.xlsx', sheet_name='Insumos', index=False)

# Display the DataFrame
# updateNutritionalValuesInSupplies()