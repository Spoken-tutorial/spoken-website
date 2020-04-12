import { Component, OnInit, Input, ElementRef, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import { CommentsService } from '../../_service/comments.service';
import { RevisionsService } from '../../_service/revisions.service';
import { AuthService } from 'src/app/_service/auth.service';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import Swal from 'sweetalert2'

@Component({
  selector: 'app-script-view',
  templateUrl: './script-view.component.html',
  styleUrls: ['./script-view.component.sass'],
})

export class ScriptViewComponent implements OnInit {
  public slides: any = [];
  public tutorials: any = [];
  private tid: number;
  private lid: number;
  private vid: number;
  public comment = false;
  public revision = false;
  public comments: any = [];
  public revisions: any;
  public tutorialName: any;
  public slideId: number;
  public slideIdRev: number;
  public index: number = 0;
  public index2: number = -1;
  public overVal: boolean[] = [false];
  public revision_old;
  public revision_new;
  public leftContentCue = "";
  public leftContentNarration = "";
  public rightContentCue = "";
  public rightContentNarration = "";
  public script: any = {};

  @Input() nav: any;
  @ViewChild('tableRow') el: ElementRef;
  @ViewChild('newmodal') el2: ElementRef;
  @ViewChild('viewScript') el3: ElementRef;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public commentsService: CommentsService,
    public revisionsService: RevisionsService,
    public router: Router,
    public authService: AuthService
  ) { }

  public viewScript() {
    this.createscriptService.getScript(
      this.tid, this.lid, this.vid
    ).subscribe(
      (res) => {
        this.slides = res['slides'];
        this.script = res;
      },
      console.error
    );
  }

  public onPublishChange(status) {
    this.createscriptService.changeScriptStatus(this.tid, this.lid, this.vid, status)
      .subscribe(
        (res) => {
          this.script.status = res['status'];
        },
        console.error
      );
  }

  public saveSuggestedTitle(title) {
    Swal.fire({
      title: 'Suggest a title for this tutorial',
      input: 'text',
      inputValue: title,
      inputAttributes: {
        autocapitalize: 'off'
      },
      showCancelButton: true,
      confirmButtonText: 'Update',
      showLoaderOnConfirm: true,
      allowOutsideClick: () => !Swal.isLoading()
    })
    .then((result) => {
      if (result.value) {
        this.createscriptService.suggestTutorialTitle(this.tid, this.lid, this.vid, `${result.value}`)
          .subscribe(
            (res) => {
              this.script.suggested_title = res['suggested_title'];
            },
            console.error
          );
      }
    })
  }

  public printSaveScript() {
    var tableContent = this.el3.nativeElement.innerHTML;
    var win = window.open('', '', 'height=500, width=500');
    win.document.write(tableContent);
    win.document.close();
    win.print();
    win.close();
  }

  public downloadPdf() {
    const doc = new jsPDF();
    doc.autoTable({
      html: '#script-table'
    });
    doc.save(`${this.tutorialName}.pdf`);
  }
  // to get hover effect on particular table rows
  public mouseenter(i) {
    this.overVal[i] = true;
  }

  public mouseleave(i) {
    this.overVal[i] = false;
  }

  public getComment() {
    this.commentsService.getComment(
      this.slideId
    ).subscribe(
      (res) => {
        this.comments = res;
      },
    );
  }

  public postComment(comment) {
    this.commentsService.postComment(
      this.slideId,
      {
        "comment": comment
      }
    ).subscribe(
      (res) => this.getComment(),
      console.error
    );
    // this.getComment();
    // this.getComment();
  }

  public viewComment(i) {
    this.el.nativeElement.querySelectorAll('tr')[this.index + 1].classList.remove('is-selected')
    this.index = i
    if (this.slideId != this.slides[i]['id']) {
      this.slideId = this.slides[i]['id']
      this.getComment();
      if (this.revision == true) {
        this.revision = false;
      }
      this.comment = true;
      this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
    }
    else {
      if (this.comment == false) {
        if (this.revision == true) {
          this.revision = false;
        }
        this.comment = true;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
      }
      else {
        this.comment = false;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.remove('is-selected')
      }
    }
  }

  public viewModal(index) {
    this.index2 = index;

    // providing current and previous version of particular slide to get the diff b/w them
    if (index == this.revisions.length - 1) {
      this.leftContentCue = "";
      this.rightContentCue = this.revisions[index]['cue'];
      this.leftContentNarration = "";
      this.rightContentNarration = this.revisions[index]['narration'];
    }
    else {
      this.leftContentCue = this.revisions[index + 1]['cue'];
      this.rightContentCue = this.revisions[index]['cue'];
      this.leftContentNarration = this.revisions[index + 1]['narration'];
      this.rightContentNarration = this.revisions[index]['narration'];
    }

    this.el2.nativeElement.classList.add('is-active')
  }

  public hideModal() {
    this.el2.nativeElement.classList.remove('is-active')
  }

  public getRevison(i) {
    this.revisionsService.getRevisions(
      i
    ).subscribe(
      (res) => {
        this.revisions = res;
        this.revision_new = res;
        if (this.revisions.length == 0) {
          this.revisions = false;
        }
      },
    );
  }

  public viewRevision(i, slidePK) {
    this.el.nativeElement.querySelectorAll('tr')[this.index + 1].classList.remove('is-selected');
    this.index = i
    if (this.slideIdRev != slidePK) {
      this.slideIdRev = slidePK
      this.getRevison(slidePK);
      if (this.comment == true) {
        this.comment = false;
      }
      this.revision = true;
      this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
    }
    else {
      if (this.revision == false) {
        if (this.comment == true) {
          this.comment = false;
        }
        this.revision = true;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.add('is-selected')
      }
      else {
        this.revision = false;
        this.el.nativeElement.querySelectorAll('tr')[i + 1].classList.remove('is-selected')
      }
    }
  }

  public revert(reversionData) {
    this.revisionsService.revertRevision(
      reversionData['id'], reversionData['reversion_id']
    ).subscribe();

    window.location.reload();
  }

  public onScriptVersionChange(vid){
    this.router.navigate(['/view/' + this.tid + '/' + this.lid + '/' + this.tutorialName + '/' + vid]);
    this.createscriptService.getScript(
      this.tid, this.lid, vid
    ).subscribe(
      (res) => {
        this.slides = res['slides'];
        this.script = res;
      },
      console.error
    );
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.tid = +params['tid'];
    });
    this.lid = this.route.snapshot.params['lid'];
    this.tutorialName = this.route.snapshot.params['tutorialName'];
    this.vid = this.route.snapshot.params['vid'];
    this.viewScript();
  }

}
