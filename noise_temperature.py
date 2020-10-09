"""
Alexis Morvan 2020-10-09

Calculate the temperature noise along the lines. following the lines of J. Gabelli's thesis, p 49, https://tel.archives-ouvertes.fr/tel-00011619/document

"""


def calculate_noise_temperature(temperature, attenuation):
    """ calculate the noise temperature """

    # room temperature
    t_noise = [300]

    # loop through all the stages
    for att, t in zip(attenuation, temperature):

        # convert dB into watt
        D = 10**(-att/20.0)

        # calculate black body noise temperature
        t_noise.append(t_noise[-1]*D**2 + (1-D**2)*t)

    return t_noise


if __name__ == "__main__":

    # temperature stages
    temperature = [50, 4, 1, 0.1, 0.001]

    # Readout line attenuation
    attenuation = [0, 20, 20, 0, 40]

    # calculate the noise at each plate
    t_noise = calculate_noise_temperature(temperature, attenuation)

    print(f'Readout noise temperature: {t_noise[-1]*1e3:0.02f} mK')

    # Control line attenuation
    attenuation = [0, 20, 10, 3, 23]

    # calculate the noise at each plate
    t_noise = calculate_noise_temperature(temperature, attenuation)

    print(f'Control noise temperature: {t_noise[-1]*1e3:0.02f} mK')
