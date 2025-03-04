"""
Statistics tracking and logging for the A-Life simulation.
"""

def calc_traits_avg(org_list):
    """
    Calculate average of genetic traits across a list of organisms.
    Returns a tuple of (speed, generation, metabolism, vision) averages.
    """
    if not org_list:
        return (0, 0, 0, 0)
    sp = sum(o.speed for o in org_list) / len(org_list)
    gn = sum(o.generation for o in org_list) / len(org_list)
    mt = sum(o.metabolism for o in org_list) / len(org_list)
    vs = sum(o.vision for o in org_list) / len(org_list)
    return (sp, gn, mt, vs)

def log_and_print_stats(t, producers, herbivores, carnivores, omnivores, csv_writer):
    """
    Log statistics to CSV and print to console.
    """
    p_count = len(producers)

    h_count = len(herbivores)
    (h_sp, h_gen, h_met, h_vis) = calc_traits_avg(herbivores)

    c_count = len(carnivores)
    (c_sp, c_gen, c_met, c_vis) = calc_traits_avg(carnivores)

    o_count = len(omnivores)
    (o_sp, o_gen, o_met, o_vis) = calc_traits_avg(omnivores)

    csv_writer.writerow([
        t, p_count, h_count, c_count, o_count,
        h_sp, h_gen, h_met, h_vis,
        c_sp, c_gen, c_met, c_vis,
        o_sp, o_gen, o_met, o_vis
    ])

    print(
        f"Timestep {t}: "
        f"P={p_count}, H={h_count}, C={c_count}, O={o_count}, "
        f"Hsp={h_sp:.2f},Hgen={h_gen:.2f},Hmet={h_met:.2f},Hvis={h_vis:.2f}, "
        f"Csp={c_sp:.2f},Cgen={c_gen:.2f},Cmet={c_met:.2f},Cvis={c_vis:.2f}, "
        f"Osp={o_sp:.2f},Ogen={o_gen:.2f},Omet={o_met:.2f},Ovis={o_vis:.2f}"
    )
