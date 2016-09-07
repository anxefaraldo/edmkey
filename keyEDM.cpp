/*************************************************************************

 Compute Angel's key estimation algos

 *************************************************************************/

void SongAnalyzer::computeAngelKeyEstimation(const std::string & audio_filename)

{

    

    const std::string kAngel = "angel.";

    // Set up constants for this analysis run

    const essentia::Real frameSize = 4096;

    const essentia::Real hopSize = 4096;

    const essentia::Real minFreq = 25;

    const essentia::Real maxFreq = 3500;

    const essentia::Real spectralPeaksThreshold = 0.0001;

    const essentia::Real spectralPeaksMax = 60;

    const essentia::Real startTime = 0;

    const essentia::Real endTime = 10e6;

    const essentia::Real sampleRate = 44100.0;

    const essentia::Real hpcpNumHarmonics = 4;

    const essentia::Real hpcpSize = 36;

    

    const essentia::Real highpassCutoff = 200;

    

    const bool hpcpBandPreset = false;

    const bool hpcpNonLinear = true;

    

    const std::string hpcpWeightType = "cosine";

    const std::string keyProfileType = "bmtg3";


    // Create the pool to store our results

    

    essentia::Pool pool;

    

    // Create our algo factory

    essentia::streaming::AlgorithmFactory& factory = essentia::streaming::AlgorithmFactory::instance();

    

    

    // create our audio reader

    essentia::streaming::Algorithm* audio = factory.create("MonoLoader",

                                                             "filename",   audio_filename.c_str(),

                                                             "sampleRate", sampleRate);

    

    essentia::streaming::Algorithm* high_pass = factory.create("HighPass",

                                                               "sampleRate", sampleRate,

                                                               "cutoffFrequency",   highpassCutoff);

    

    essentia::streaming::Algorithm* frame_cutter = factory.create("FrameCutter",

                                                           "frameSize",   frameSize,

                                                           "hopSize", hopSize);

    

    

    

    

    essentia::streaming::Algorithm* windowing = factory.create("Windowing",

                                                               "size", frameSize);

    

    

    

    essentia::streaming::Algorithm* spectrum = factory.create("Spectrum",

                                                               "size", frameSize);

    

    essentia::streaming::Algorithm* spectral_whitening = factory.create("SpectralWhitening",

                                                                        "maxFrequency", maxFreq,

                                                                        "sampleRate", sampleRate);

    

    essentia::streaming::Algorithm* spectral_peaks = factory.create("SpectralPeaks",

                                                                    "magnitudeThreshold", spectralPeaksThreshold,

                                                                    "maxPeaks", spectralPeaksMax,

                                                                    "maxFrequency", maxFreq,

                                                                    "minFrequency", minFreq,

                                                                    "sampleRate", sampleRate);

    

    

    // HPCP Key

    essentia::streaming::Algorithm* hpcp_key = factory.create("HPCP",

                                                              "size", hpcpSize,

                                                              "harmonics", hpcpNumHarmonics,

                                                              "bandPreset", hpcpBandPreset,

                                                              "minFrequency", minFreq,

                                                              "maxFrequency", maxFreq,

                                                              "weightType", hpcpWeightType,

                                                              "nonLinear", hpcpNonLinear);

    

    essentia::streaming::Algorithm* key_edm3 = factory.create("KeyEDM3",

                                                              "profileType", keyProfileType,

                                                              "pcpSize", hpcpSize);

    

    

    essentia::streaming::connect(audio->output("audio"), high_pass->input("signal"));

    essentia::streaming::connect(high_pass->output("signal"), frame_cutter->input("signal"));

    essentia::streaming::connect(frame_cutter->output("frame"), windowing->input("frame"));

    essentia::streaming::connect(windowing->output("frame"), spectrum->input("frame"));

    

    // Store values in pool

    //connect(spectrum->output("spectrum"), pool, kAngel + "spectrum");

    //connect(spectral_peaks->output("spectrum"), pool, kRhythm + "beats_loudness");

    essentia::streaming::connect(spectrum->output("spectrum"), spectral_peaks->input("spectrum"));

    essentia::streaming::connect(spectrum->output("spectrum"), spectral_whitening->input("spectrum"));

    essentia::streaming::connect(spectral_peaks->output("frequencies"), spectral_whitening->input("frequencies"));

    essentia::streaming::connect(spectral_peaks->output("magnitudes"), spectral_whitening->input("magnitudes"));

    

    essentia::streaming::connect(spectral_peaks->output("frequencies"), hpcp_key->input("frequencies"));

    essentia::streaming::connect(spectral_whitening->output("magnitudes"), hpcp_key->input("magnitudes"));

    

    

    // What we need to do here is accumulate frames for bar and for beat and then

    // derive key estimations for each bar AND each beat...

    essentia::streaming::connect(hpcp_key->output("hpcp"), key_edm3->input("pcp"));

    

    connect(key_edm3->output("key"), pool, kAngel + "key");

    connect(key_edm3->output("scale"), pool, kAngel + "scale");

    connect(key_edm3->output("strength"), pool, kAngel + "strength");


    

    

    essentia::scheduler::Network network_angel(audio);

    

    network_angel.run();


    LogD(TAG, "Did it work?");


}
