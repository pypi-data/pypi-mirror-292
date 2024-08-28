# Autolingua
Automated linguistic codification python package used in [[1]](https://doi.org/10.19130/iifl.adel.2022.10.2.X00S25872)

## Installation

To install the package, run the following commands:

```bash
git clone https://github.com/ramajoballester/autolingua.git
cd autolingua
pip install -e .
```

Once installed, you can run the package by typing `autolingua <command>` in the terminal from every directory. Please run `autolingua -h` to check the available commands.

# Automatic variable codification

Automatic codification script. Run ```autolingua codification -h``` to check the program settings.

Run it from the directory where the input files are located.

```bash
autolingua codification -init_cell D446 -file_name PRESEEA_1995_Nivel_bajo.xlsx -color
```


# PULSO project automatic lemmatization

Automatic lemmatization replacement script. Run ```autolingua lemmatization -h``` to check the program settings.

Run it from the directory where the input Excel files are located.

```bash
autolingua replacement -fases_filename filename -input_filename filename 
```

For sequential fase data loading:

```bash
autolingua replacement -fases_filename filename -input_filename filename -fase2_from_file filename -fase3_from_file filename
```


# References

[1] Ávila, A. M., Segura, A. (2022). Estudio de las variables predictoras de la expresión del sujeto pronominal en el corpus PRESEEA. Málaga. Nivel de instrucción bajo, Anuario de Letras. Lingüística y Filología, vol. 10, no. 2, pp.57–93. doi:10.19130/iifl.adel.2022.10.2.X00S25872

# Citation

If you use this repository, please cite:

Ramajo-Ballester, Á. (2022). Autolingua repository, GitHub. https://github.com/ramajoballester/autolingua
