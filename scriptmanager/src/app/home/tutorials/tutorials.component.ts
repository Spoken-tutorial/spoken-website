import { Component, OnInit, Input } from '@angular/core';
import { TutorialsService } from '../../_service/tutorials.service'
import { Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import { environment} from '../../../environments/environment';

@Component({
  selector: 'app-tutorials',
  templateUrl: './tutorials.component.html',
  styleUrls: ['./tutorials.component.sass']
})
export class TutorialsComponent implements OnInit {
  public env =  environment;
  public scriptVersionsAllowed = this.env['scriptVersionsAllowed'];

  @Input() tutorial: any;

  constructor(
    public tutorialService: TutorialsService,
    public createscriptService: CreateScriptService,
    public router: Router
  ) { }

  public onClickCreate(){
    this.router.navigate(['ScriptCreateComponent']);
  }

  public reupload(tid, lid, tutorialName, vid, isDelete){
    if (isDelete) {
      this.createscriptService.deleteScriptVersion(tid, lid, vid).subscribe(
        (res) => {
          new Noty({
            type: 'success',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'The slide is sucessfully deleted!',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        },
        (error) => {
          new Noty({
            type: 'error',
            layout: 'topRight',
            theme: 'metroui',
            closeWith: ['click'],
            text: 'Woops! There seems to be an error.',
            animation: {
              open: 'animated fadeInRight',
              close: 'animated fadeOutRight'
            },
            timeout: 4000,
            killer: true
          }).show();
        }
      );
      this.router.navigate(['/upload/' + tid + '/' + lid + '/' + tutorialName + '/' + vid]);
    }
    else {
      const version = +vid + 1;
      this.router.navigate(['/upload/' + tid + '/' + lid + '/' + tutorialName + '/' + version]);
    }
  }

  ngOnInit() {
  }

}
