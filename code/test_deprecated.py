def test_pipeline(logger): #deprecated
    DIRECTORY = TEST_DIRECTORY + sep + "test_pipeline"
    LANGUAGE = "de"

    assert not exists(DIRECTORY)
    
    FILEPATH = DIRECTORY + sep + TITLE + "_" + LANGUAGE

    logger.start("Testing pipeline...")
    
    #scrape article
    with Scraper(logger = logger, title = TITLE, language = LANGUAGE) as scraper:
        scraper.scrape(DIRECTORY)

    #load article from file
    article = Article(FILEPATH)
    article.plot_revision_distribution_to_file(DIRECTORY)

    #load bibliography from file
    bibliography = Bibliography(".." + sep + "data" + sep + "tracing-innovations-lit.bib")
    bibliography.plot_publication_distribution_to_file(DIRECTORY)

    #track bibkeys and print/plot
    tracks = article.track_field_values_in_article(["titles", "dois", "authors"], bibliography)
    for track in tracks.items():
        article.write_track_to_file(track, DIRECTORY)
        article.plot_track_to_file(track, DIRECTORY)

    #assert revision information
    assert article.revisions[0].revid == 69137443
    assert article.revisions[0].timestamp_pretty_string() == "2010-01-11 02:11:54"
    assert article.revisions[0].user == "Tinz"
    assert article.revisions[0].userid == 92881
    assert article.revisions[0].comment == "neu, wird noch erweitert"

    rmtree(DIRECTORY)

    logger.stop("Pipeline test successful.", 1)
