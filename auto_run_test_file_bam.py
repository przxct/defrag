import os
import subprocess
import time

def process_file(bam, bamdir, outfile):
    prefix = os.path.basename(bam).rsplit('.', 1)[0]
    print(bam)
    print(bamdir)
    print(prefix)

    # Sort and process with Picard
    subprocess.call([
    'java', '-jar', '/Users/nguyenngocanh/Downloads/picard.jar', 'SortSam',
    'INPUT=' + bam,              # Input SAM/BAM file
    'OUTPUT=' + bamdir + prefix + '.sorted.bam',      # Output sorted BAM file
    'SORT_ORDER=coordinate',                 # Sort order (coordinate in this case)
    'CREATE_INDEX=true'                     # Create an index for the sorted BAM file
    ])

    # Filter reads with Samtools
    subprocess.call(['samtools', 'rmdup', '-s', bamdir + prefix + '.sorted.bam', bamdir + prefix + '.filtered.bam'])

    # Convert .bam to .pickle
    samtools_view_command = ['samtools', 'view', bamdir + prefix + '.filtered.bam', '-q', '1']
    consam_command = ['python3', 'consam_bam.py', '-outfile', outfile + prefix + '.pickle', '-binsize', '50000']
    samtools_view_process = subprocess.Popen(samtools_view_command, stdout=subprocess.PIPE)
    consam_process = subprocess.Popen(consam_command, stdin=samtools_view_process.stdout)
    samtools_view_process.stdout.close()
    consam_process.communicate()

    # Move the final result to the specified outfile
    # shutil.move(bamdir + prefix + '.pickle', outfile)

    # subprocess.call(['samtools', 'rmdup', '-s', bam, '-', '|', 'samtools', 'view', '-', '-q', '1', '|', 'python', 'consam.py', '-outfile', FASTQ_DIR + prefix + '.pickle'])

    # Apply GC-correction
    subprocess.call(['python3', 'gcc.py', outfile + prefix + '.pickle', './ref/gccount', outfile + prefix + '.gcc', '-binsize', '50000'])

    # os.remove(prefix + '.sai')
    os.remove(bamdir + prefix + '.sorted.bam')
    os.remove(bamdir + prefix + '.sorted.bai')
    os.remove(bamdir + prefix + '.filtered.bam')

def main():
    REFERENCE = "./reference/hg19.fa"
    REF_DIR = "./ref"
    directories = ["/Users/nguyenngocanh/Desktop/lab/seqff/real_data/server/"]
    outfile = "./temp/"

    # record start time
    start = time.time()
    for directory in directories:
        print("path file: " + directory)
        for filename in os.listdir(directory):
            file_pickle = os.path.join(outfile, filename.split(".")[0] + ".pickle")
            if filename.endswith(".bam") and os.path.isfile(file_pickle) is False:
                process_file(os.path.join(directory, filename), directory, outfile)

    subprocess.call(['python3', 'defrag_to_log_ff.py', './boydir', './girldir', './temp/', './output/figure'])

    # record end time
    end = time.time()
    print("The time of execution of ", len(os.listdir(directories[0])), " tests is :",
        (end - start) / 60, "min")

if __name__ == '__main__':
    main()

