def generate_levels(mean, sigma, sigma_list):
    return [mean + sigma * x for x in sigma_list]
