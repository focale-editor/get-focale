#import <Foundation/Foundation.h>
#include <dlfcn.h>
#include <sys/xattr.h>

/// The stable ONNX entry point needed to verify that the runtime can initialize.
struct OrtApiBase {
  const void *(*GetApi)(uint32_t);
  const char *(*GetVersionString)(void);
};

/// Download and load native code with sandbox and library validation enabled.
int main(int argc, char **argv) {
  @autoreleasepool {
    if (argc != 2) return 2;
    NSError *error = nil;
    NSURL *file;
    if (strcmp(argv[1], "bundled") == 0) {
      file = [[NSBundle mainBundle].privateFrameworksURL
          URLByAppendingPathComponent:@"libonnxruntime.dylib"];
    } else {
      NSURL *directory = [[[NSFileManager defaultManager]
          URLsForDirectory:NSApplicationSupportDirectory
          inDomains:NSUserDomainMask] firstObject];
      directory = [directory URLByAppendingPathComponent:@"runtime-probe" isDirectory:YES];
      if (![[NSFileManager defaultManager] createDirectoryAtURL:directory
          withIntermediateDirectories:YES attributes:nil error:&error]) {
        NSLog(@"%@", error);
        return 3;
      }
      file = [directory URLByAppendingPathComponent:@"libonnxruntime.dylib"];
      if (strcmp(argv[1], "offline") != 0) {
        NSData *data = [NSData dataWithContentsOfURL:[NSURL URLWithString:@(argv[1])]
            options:0 error:&error];
        if (!data || ![data writeToURL:file options:NSDataWritingAtomic error:&error]) {
          NSLog(@"%@", error);
          return 4;
        }
      }
    }
    char quarantine[1024] = {0};
    ssize_t length = getxattr(file.path.fileSystemRepresentation,
        "com.apple.quarantine", quarantine, sizeof(quarantine) - 1, 0, 0);
    printf("file=%s\nquarantine=%s\n", file.path.UTF8String,
        length >= 0 ? quarantine : "absent");
    fflush(stdout);
    void *handle = dlopen(file.path.fileSystemRepresentation, RTLD_NOW | RTLD_LOCAL);
    if (!handle) {
      fprintf(stderr, "%s\n", dlerror());
      return 5;
    }
    const struct OrtApiBase *(*getBase)(void) = dlsym(handle, "OrtGetApiBase");
    if (!getBase || !getBase()->GetApi(18)) return 6;
    printf("loaded=%s\n", getBase()->GetVersionString());
    dlclose(handle);
    return 0;
  }
}
