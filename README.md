# File Transfer

# Redes - FIUBA

# Trabajo Práctico Nº 1

| Padrón | Alumno |
|--------| ------ |
|  96467 | Chávez Cabanillas, José Eduardo |
|  96015 | Elias, Federico                 |
| 106171 | Davico, Mauricio                |
| 104554 | Hoszowski, Luciana              |
| 104557 | Hoszowski, Juan                 |

# Tabla de contenidos

- [Requerimientos](#requerimientos) 
    - [Python](#python)
    - [Sistema Operativo](#sistema-operativo) 
- [Guía de Uso](#guía-de-uso)
    - [Cliente](#clientes)
    - [Servidor](#servidor)
    - [Lista de argumentos](#lista-de-argumentos)
- [Mininet](#mininet)
    - [Recomendación](#recomendación)

# Requerimientos

## Python:
Para ejecutar este proyecto, necesitarás tener instalado Python *3.10* o una versión superior. Puedes verificar la versión de Python instalada en tu sistema ejecutando el siguiente comando en tu terminal:

```
python --version
```

Si no tienes Python instalado o necesitas actualizarlo, por favor visita [python.org](https://www.python.org).

## Sistema operativo
Compatible con cualquier distribución de Linux. Este proyecto está diseñado para ser ejeutado en sistemas Linux. Asegurate de tener una distribución de Linux instalada para utilizar este proyecto.

# Guía de uso

## Clientes

Para ejecutar cualquiera de los dos clientes UPLOAD o DOWNLOAD se debe ingresar los siguientes comandos por la terminal

```bash
    # Upload
    $ python3 upload.py [-v | -q] -H <ip> -p <port> -s <path-file> -n <name-file> [-sw | -sr] 
    
    # Download
    $ python3 download.py [-v | -q] -H <ip> -p <port> -d <path-file> -n <name-file> [-sw | -sr] 
```
## Servidor

Para el servidor se debe ingresar el siguiente comando
```bash
    # Server
    $ python3 start-server.py [-v | -q] -H <ip> -p <port> -s <path-file>
```

## Lista de argumentos
Teniendo en cuenta que los argumentos en comun son los siguientes
```bash
    -v  --verbose   increase output verbosity
    -q  --quiet     decrease output verbosity
    -H  --host      server IP address
    -p  --port      server port
```

Comandos especificos para los clientes y el server
```bash
    # Protocol client
    -sw --stopwait          select protocol stop and wait
    -sr --selectiverepeat   select protocol selective repeat
    # Upload
    -s  --src       source file path
    -n  --name      file name
    -m  --mininet   running all host in mininet
    # Download
    -d  --dst       destination file path
    -n  --name      file name    
    -m  --mininet   running all host in mininet
    # Server
    -s  --storage   storage dir path
```

Si se quiere consultar las opciones detalladas anteriormente, bastará con ejecutar el programa ya sea el servidor o cualquiera de los clientes

```bash
    # Upload
    $ python3 upload.py -h
    
    # Download
    $ python3 download.py -h
    
    # Server
    $ python3 start-server.py -h
```

# Mininet

Este proyecto cuenta con una topologia para su prueba con perdidas de paquetes, para lo cual se hace uso de Mininet. Por lo cual si se desea probar el proyecto con perdidas de paquetes primero se tiene que tener instalado Mininet, este se puede instalar siguiendo los pasos que se encuentran en su pagina oficial [mininet.org](https://mininet.org/download/)

Una vez instalado Mininet, para hacer uso de la topologia se debe ejecutar el siguiente comando en la terminal

```bash
    # Mininet
    $ sudo python3 mininet_topo.py
```

## Recomendación

Mininet actualmente no funciona en la version 3.12 de Python, asegurese de tener una versión de Python anterior a esta.